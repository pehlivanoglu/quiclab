"""SBD baselines DCW, rmcatSBD and dcSBD (not FlowBot itself), from
CobottleneckDetector in FlowBot src/detector.py (github.com/PrinceS17/flowbot,
commit a7a21fa). Every method below except __init__ is copied verbatim from that
class (extracted by AST); see README.md.

__init__ is quiclab's: the original requires ground-truth labels, unpickles a
scikit-learn 0.24 bottleneck classifier and sets torch threads, none of which
DCW or SBD use. It sets the same attributes the copied methods read.
"""

import numpy as np
import pandas as pd

from .cluster import cluster
from .denoise import DeNoise
from .preprocess import measure_time
from .sbd import SBDAlgorithm


class CobottleneckDetector:
    """Subset of FlowBot's CobottleneckDetector: methods 'dcw', 'rmcat_sbd',
    'dc_sbd' (and the trivial 'neg_naive' / 'pos_naive')."""

    def __init__(self, flow_df, interval, t_unit=0.005, model_th=None, max_iter=10):
        """flow_df: [run, flow, time, owd, drop, label] on a gap-free t_unit
        grid; flow ids must be integers. model_th is DCW's correlation
        threshold (the original falls back to 0.5 when unset)."""
        self.flow_df = flow_df
        assert self.flow_df[['run', 'flow', 'time']].duplicated().sum() == 0
        self.interval = interval
        self.t_unit = t_unit
        self.model_th = model_th
        self.max_iter = max_iter
        self.sbd_df = None
        self.latent_map = {}
        self.flat_flows = []
        self.ticks = None

    def classify(self, start, end, selected_dfs,
                method='dcw', use_old_sbd=False, seq_len=None):
        """Given flows' data of a period, output their group No. time series.
        Returns a list of list.
        """
        self.latent_map = {}
        if method == 'rmcat_sbd':
            return self._sbd_classify(start, end, 'rmcat', use_old=use_old_sbd)
        if method == 'dc_sbd':
            return self._sbd_classify(start, end, 'dc', use_old=use_old_sbd)

        # For DCW and ML, we want the segment to be exactly the same length of
        # interval due to the needs to utilize ML model. Thus, the 1st line below
        # is chosen and the incomplete segment in the end is discarded.
        y_hats = []
        for tick, selected in zip(self.ticks, selected_dfs):
            t0 = round(tick, 3)
            if 'label' in selected.columns:
                tmp_df = selected.drop(columns=['label'])
            y_hat, latent = self._classify_segment(tmp_df, method)
            y_hats.append(y_hat)
            self.latent_map[t0] = latent
        return y_hats

    def _sbd_classify(self, start, end, cluster_alg='dc', use_old=False):
        """SBD method from start to end.

        Since SBD has defined window internally, we call it as a whole
        to produce the full group No. time series. Cluster can be rmcat
        or dc (Chinese Whisper).
        """
        start = max(start, self.flow_df.time.min())
        end = min(end, self.flow_df.time.max())
        flow_df = self.flow_df[(self.flow_df.time >= start) & (self.flow_df.time < end - 1e-6)]
        sbd = SBDAlgorithm()
        if use_old:
            sbd_df = self.sbd_df
        else:
            sbd_df = sbd.stream_process(flow_df, t_unit=self.t_unit)

        sbd_df1 = sbd_df.drop(columns=['label'])
        if cluster_alg == 'rmcat':
            y_hats = self._rmcat_sbd_classify(sbd, sbd_df1)
        elif cluster_alg == 'dc':
            y_hats = self._dc_sbd_classify(sbd, sbd_df1)
        self.sbd_df = sbd_df
        self.ticks = sbd_df.time.unique()
        return y_hats

    def _rmcat_sbd_classify(self, sbd: SBDAlgorithm, sbd_df: pd.DataFrame):
        group_df = sbd.rmcat_clustering(sbd_df)
        group_df = group_df.sort_values(['time', 'flow']).reset_index(
                                        drop=True)
        # res = [group_df[group_df.time == t].group.tolist()
        #         for t in group_df.time.unique()]
        y_hats = []
        for i, t in enumerate(sorted(group_df.time.unique())):
            tmp_df = group_df[group_df.time == t]
            y_hat = tmp_df.group.tolist()
            self.latent_map[t] = None
            y_hats.append(y_hat.copy())
        return y_hats

    def _dc_sbd_classify(self, sbd: SBDAlgorithm, sbd_df: pd.DataFrame):
        # sbd_df: [time, flow, & skewness, variability, etc]
        y_hats = []
        sbd_df.set_index(['time'], inplace=True)
        sbd_df.sort_index(inplace=True)
        last_labels = None
        prev_btnk = {flow: False for flow in sbd_df.flow.unique()}
        for i, t in enumerate(sbd_df.index.unique()):
            seg_df = sbd_df.loc[t].copy()
            if type(seg_df) == pd.Series:   # Series is returned if only one flow
                seg_df = pd.DataFrame([seg_df])
            seg_df.sort_values(by='flow', inplace=True)
            seg_df.reset_index(inplace=True)
            if 'time' not in seg_df.columns:
                seg_df.rename(columns={'index': 'time'}, inplace=True)

            # use SBD btnk condition to first separate the non-btnk flows
            flow_labels = {flow: -1 for flow in seg_df.flow.unique()}
            f_max = max(seg_df.flow.unique())
            for ri, row in seg_df.iterrows():
                btnked = sbd.btnk_condition(row, prev_btnk[row.flow])
                prev_btnk[row.flow] = btnked
                if not btnked:
                    flow_labels[row.flow] = f_max + ri + 1

            # cluster the btnk flows
            seg_df = seg_df.drop(columns=['time', 'flow', 'd_avg'])
            # segment = torch.tensor(seg_df.to_numpy(dtype=np.float32))
            segment = seg_df.to_numpy(dtype=np.float32)
            self.latent_map[t] = segment.tolist()
            y_hat, flow_labels, _ = cluster(segment, max_iter=self.max_iter,
                                            n_voter=1, weighting='inv_sq',
                                            last_labels=last_labels,
                                            flow_labels=flow_labels)
            y_hat = y_hat.tolist()
            last_labels = flow_labels.copy()
            y_hats.append(y_hat.copy())

        sbd_df.reset_index(inplace=True)
        return y_hats

    def _get_selected_dfs(self, start, end, seq_len):
        """Get selected dfs for later usage in classify and classify_truth.
        Abstracted to maintain the consistency of the segments."""
        selected_dfs = []
        self.ticks = self._set_ticks(start, end, None)
        for tick in sorted(self.ticks):
            t0 = round(tick, 3)     # necessary for precision issue avoidance
            if t0 == self.flow_df.time.max():
                break
            selected = self._get_seg_df(self.flow_df, t0, seq_len)
            selected_dfs.append(selected)
        return selected_dfs

    def _set_ticks(self, start, end, ticks):
        start = max(start, self.flow_df.time.min())
        end = min(end, self.flow_df.time.max())
        ticks = ticks if ticks is not None else \
            [start + i * self.interval for i in range(int((end - start) / self.interval))]
        return ticks

    def _get_seg_df(self, df, t0, seq_len):
        """Ensure getting seq_len samples for each flow from t0.
        TODO: ensure head_enough is not slow for overhead test
        """
        def head_enough(df, n):
            if len(df) >= n:
                return df.head(n)
        interval = seq_len * self.t_unit
        seg_df = df[(df.time >= t0) &
                    (df.time < t0 + interval - 1e-6)].sort_values(by='time')\
                .groupby('flow', group_keys=False).apply(head_enough, seq_len)\
                .reset_index(drop=True)\
                .sort_values(by=['time', 'flow'])
        seg_df['cnt'] = seg_df.groupby('flow')['time'].transform('count')
        seg_df['t_start'] = seg_df.groupby('flow')['time'].transform('min')
        assert  seg_df.cnt.nunique() == 1, \
            f'Multiple flow count: {seg_df.cnt.unique()}'
        assert  seg_df.t_start.max() - seg_df.t_start.min() <= 0.005, \
            f'Multiple flow start time: {seg_df.t_start.unique()}'
        return seg_df

    def _classify_segment(self, segment, method):
        """Classify segments, i.e. flow df of a small period, into groups.
        Returns a list of group No. for each flow in the segment.
        """
        latent = None
        if method == 'dcw':
            res = self._dcw_classify_segment(segment)
        elif method == 'ml':
            res, latent = self._ml_classify_segment(segment)
        elif method == 'neg_naive':
            res = list(range(segment.flow.nunique()))
        elif method == 'pos_naive':
            res = [1] * segment.flow.nunique()
        else:
            raise NotImplementedError
        return res, latent

    def _dcw_classify_segment(self, segment):
        # TODO(Bowen): use pairwise flow owd correlations
        # TODO(Bowen): when using all flat signals, out is nan

        level = 6
        n_flow = segment.flow.nunique()
        th = self.model_th or 0.5

        d1 = DeNoise(segment)
        d2 = DeNoise(segment)
        flow_list = [-1 for i in range(n_flow)]
        group_number = 0
        flow_list[0] = 0

        for flow1 in range(n_flow): # how many flow we need to deal with?
            # flow 1/2 is the index, while flow 1/2_seg is the real flow number
            flow1_seg = segment.flow.unique()[flow1]
            d1.load_flow(flow1_seg)
            if d1.flow.nunique() == 1:
                # print(f' Warning: flow {flow1} has only one value, set group to NaN!')
                flow_list[flow1] = -1
                continue
            coe1 = d1.dwt(level)
            d1.threshold(coe1)
            coe1 = d1.soft_threshold(coe1)
            out1 = d1.idwt(coe1)
            for flow2 in range(flow1 + 1, n_flow):
                flow2_seg = segment.flow.unique()[flow2]
                d2.load_flow(flow2_seg)

                if d2.flow.nunique() == 1:
                    # print(f' Warning: flow {flow2} has only one value, set group to NaN!')
                    flow_list[flow2] = -1
                    continue
                coe2 = d2.dwt(level)
                d2.threshold(coe2)
                coe2 = d2.soft_threshold(coe2)
                out2 = d2.idwt(coe2)
                std1 = np.std(out1) if np.std(out1) else 1
                std2 = np.std(out2) if np.std(out2) else 1
                # assert np.std(out1) != 0 and np.std(out2) != 0, \
                #     f'flow {flow1} and {flow2} has std 0 in out!'
                assert not (np.isnan(std1) or np.isnan(std2)), \
                    f'flow {flow1} and {flow2} has NaN in out!'
                out1 = (out1 - np.mean(out1)) / (std1 * len(out1))
                out2 = (out2 - np.mean(out2)) / (std2)
                result = np.correlate(out1, out2)
                if result[0] > th:
                    if flow_list[flow2] == -1:
                        flow_list[flow2] = flow_list[flow1]
                    else:
                        flow_list[flow1] = min(flow_list[flow1], flow_list[flow2])
                        flow_list[flow2] = min(flow_list[flow1], flow_list[flow2])
                elif flow_list[flow2] == -1:
                    group_number = group_number + 1
                    flow_list[flow2] = group_number
        for flow1 in range(n_flow):
            if flow_list[flow1] == -1:
                group_number += 1
                flow_list[flow1] = group_number

        return flow_list

    def get_sbd_df(self):
        """None if method is not SBD family."""
        return self.sbd_df
