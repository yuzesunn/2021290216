# Experiment framework
import operator
import random
from collections import defaultdict
from typing import Any, Callable, Optional

import numpy as np
from compressors import DefaultCompressor
from tqdm import tqdm


class KnnExpText:
    def __init__(
        self,
        aggregation_function: Callable,
        compressor: DefaultCompressor,
        distance_function: Callable,
    ) -> None:
        self.aggregation_func = aggregation_function
        self.compressor = compressor
        self.distance_func = distance_function
        self.distance_matrix: list = []

    def calc_dis(
        self, data: list, train_data: Optional[list] = None, fast: bool = False
    ) -> None:
        """
        Calculates the distance between either `data` and itself or `data` and
        `train_data` and appends the distance to `self.distance_matrix`.

        Arguments:
            data (list): Data to compute distance between.
            train_data (list): [Optional] Training data to compute distance from `data`.
            fast (bool): [Optional] Uses the _fast compression length function
                                    of `self.compressor`.

        Returns:
            None: None
        """

        data_to_compare = data
        if train_data is not None:
            data_to_compare = train_data

        for i, t1 in tqdm(enumerate(data)):
            distance4i = []
            if fast:
                t1_compressed = self.compressor.get_compressed_len_fast(t1)
            else:
                t1_compressed = self.compressor.get_compressed_len(t1)
            for j, t2 in enumerate(data_to_compare):
                if fast:
                    t2_compressed = self.compressor.get_compressed_len_fast(t2)
                    t1t2_compressed = self.compressor.get_compressed_len_fast(
                        self.aggregation_func(t1, t2)
                    )
                else:
                    t2_compressed = self.compressor.get_compressed_len(t2)
                    t1t2_compressed = self.compressor.get_compressed_len(
                        self.aggregation_func(t1, t2)
                    )
                distance = self.distance_func(
                    t1_compressed, t2_compressed, t1t2_compressed
                )
                distance4i.append(distance)
            self.distance_matrix.append(distance4i)

    def calc_dis_with_single_compressed_given(
        self, data: list, data_len: list = None, train_data: Optional[list] = None
    ) -> None:
        """
        Calculates the distance between either `data`, `data_len`, or
        `train_data` and appends the distance to `self.distance_matrix`.

        Arguments:
            data (list): Data to compute distance between.
            train_data (list): [Optional] Training data to compute distance from `data`.
            fast (bool): [Optional] Uses the _fast compression length function
                                    of `self.compressor`.

        Returns:
            None: None
        """

        data_to_compare = data
        if train_data is not None:
            data_to_compare = train_data

        for i, t1 in tqdm(enumerate(data)):
            distance4i = []
            t1_compressed = self.compressor.get_compressed_len_given_prob(
                t1, data_len[i]
            )
            for j, t2 in tqdm(enumerate(data_to_compare)):
                t2_compressed = self.compressor.get_compressed_len_given_prob(
                    t2, data_len[j]
                )
                t1t2_compressed = self.compressor.get_compressed_len(
                    self.aggregation_func(t1, t2)
                )
                distance = self.distance_func(
                    t1_compressed, t2_compressed, t1t2_compressed
                )
                distance4i.append(distance)
            self.distance_matrix.append(distance4i)

    def calc_dis_single(self, t1: str, t2: str) -> float:
        """
        Calculates the distance between `t1` and `t2` and returns
        that distance value as a float-like object.

        Arguments:
            t1 (str): Data 1.
            t2 (str): Data 2.

        Returns:
            float-like: Distance between `t1` and `t2`.
        """

        t1_compressed = self.compressor.get_compressed_len(t1)
        t2_compressed = self.compressor.get_compressed_len(t2)
        t1t2_compressed = self.compressor.get_compressed_len(
            self.aggregation_func(t1, t2)
        )
        distance = self.distance_func(t1_compressed, t2_compressed, t1t2_compressed)
        return distance

    def calc_dis_single_multi(self, train_data: list, datum: str) -> list:
        """
        Calculates the distance between `train_data` and `datum` and returns
        that distance value as a float-like object.

        Arguments:
            train_data (list): Training data as a list-like object.
            datum (str): Data to compare against `train_data`.

        Returns:
            list: Distance between `t1` and `t2`.
        """

        distance4i = []
        t1_compressed = self.compressor.get_compressed_len(datum)
        for j, t2 in tqdm(enumerate(train_data)):
            t2_compressed = self.compressor.get_compressed_len(t2)
            t1t2_compressed = self.compressor.get_compressed_len(
                self.aggregation_func(datum, t2)
            )
            distance = self.distance_func(t1_compressed, t2_compressed, t1t2_compressed)
            distance4i.append(distance)
        return distance4i

    def calc_dis_with_vector(self, data: list, train_data: Optional[list] = None):
        """
        Calculates the distance between `train_data` and `data` and returns
        that distance value as a float-like object.

        Arguments:
            train_data (list): Training data as a list-like object.
            datum (str): Data to compare against `train_data`.

        Returns:
            float-like: Distance between `t1` and `t2`.
        """

        if train_data is not None:
            data_to_compare = train_data
        else:
            data_to_compare = data
        for i, t1 in tqdm(enumerate(data)):
            distance4i = []
            for j, t2 in enumerate(data_to_compare):
                distance = self.distance_func(t1, t2)
                distance4i.append(distance)
            self.distance_matrix.append(distance4i)

    def calc_acc(
        self,
        k: int,
        label: list,
        train_label: Optional[list] = None,
        provided_distance_matrix: Optional[list] = None,
        rand: bool = False,
    ) -> tuple:
        """
        Calculates the accuracy of the algorithm.

        Arguments:
            k (int?): TODO
            label (list): Predicted Labels.
            train_label (list): Correct Labels.
            provided_distance_matrix (list): Calculated Distance Matrix to use
                                             instead of `self.distance_matrix`.
            rand (bool): TODO

        Returns:
            tuple: predictions, and list of bools indicating prediction correctness.

        """
        if provided_distance_matrix is not None:
            self.distance_matrix = provided_distance_matrix
        correct = []
        pred = []
        if train_label is not None:
            compare_label = train_label
            start = 0
            end = k
        else:
            compare_label = label
            start = 1
            end = k + 1

        for i in range(len(self.distance_matrix)):
            sorted_idx = np.argsort(np.array(self.distance_matrix[i]))
            pred_labels = defaultdict(int)
            for j in range(start, end):
                pred_l = compare_label[sorted_idx[j]]
                pred_labels[pred_l] += 1
            sorted_pred_lab = sorted(
                pred_labels.items(), key=operator.itemgetter(1), reverse=True
            )
            most_count = sorted_pred_lab[0][1]
            if_right = 0
            most_label = sorted_pred_lab[0][0]
            most_voted_labels = []
            for pair in sorted_pred_lab:
                if pair[1] < most_count:
                    break
                if not rand:
                    if pair[0] == label[i]:
                        if_right = 1
                        most_label = pair[0]
                else:
                    most_voted_labels.append(pair[0])
            if rand:
                most_label = random.choice(most_voted_labels)
                if_right = 1 if most_label == label[i] else 0
            pred.append(most_label)
            correct.append(if_right)
        print("Accuracy is {}".format(sum(correct) / len(correct)))
        return pred, correct

    def combine_dis_acc(
        self,
        k: int,
        data: list,
        label: list,
        train_data: Optional[list] = None,
        train_label: Optional[list] = None,
    ) -> tuple:
        """
        Calculates the distance and the accuracy of the algorithm for data with
        training.

        Arguments:
            k (int?): TODO
            data (list): Data used for predictions.
            label (list): Predicted Labels.
            train_data (list): Training data to compare distances.
            train_label (list): Correct Labels.

        Returns:
            tuple: predictions, and list of bools indicating prediction correctness.
        """
        correct = []
        pred = []
        if train_label is not None:
            compare_label = train_label
            start = 0
            end = k
        else:
            compare_label = label
            start = 1
            end = k + 1
        if train_data is not None:
            data_to_compare = train_data
        else:
            data_to_compare = data
        for i, t1 in tqdm(enumerate(data)):
            distance4i = self.calc_dis_single_multi(data_to_compare, t1)
            sorted_idx = np.argsort(np.array(distance4i))
            pred_labels = defaultdict(int)
            for j in range(start, end):
                pred_l = compare_label[sorted_idx[j]]
                pred_labels[pred_l] += 1
            sorted_pred_lab = sorted(
                pred_labels.items(), key=operator.itemgetter(1), reverse=True
            )
            most_count = sorted_pred_lab[0][1]
            if_right = 0
            most_label = sorted_pred_lab[0][0]
            for pair in sorted_pred_lab:
                if pair[1] < most_count:
                    break
                if pair[0] == label[i]:
                    if_right = 1
                    most_label = pair[0]
            pred.append(most_label)
            correct.append(if_right)
        print("Accuracy is {}".format(sum(correct) / len(correct)))
        return pred, correct

    def combine_dis_acc_single(
        self,
        k: int,
        train_data: list,
        train_label: list,
        datum: str,
        label: Any,  # int, as used in this application
    ) -> tuple:
        """
        Calculates the distance and the accuracy of the algorithm for a single
        datum with training.

        Arguments:
            k (int?): TODO
            train_data (list): Training data to compare distances.
            train_label (list): Correct Labels.
            datum (str): Datum used for predictions.
            label (Any): Correct label of datum.

        Returns:
            tuple: prediction, and a bool indicating prediction correctness.
        """
        # Support multi processing - must provide train data and train label
        distance4i = self.calc_dis_single_multi(train_data, datum)
        sorted_idx = np.argpartition(np.array(distance4i), range(k))
        pred_labels = defaultdict(int)
        for j in range(k):
            pred_l = train_label[sorted_idx[j]]
            pred_labels[pred_l] += 1
        sorted_pred_lab = sorted(
            pred_labels.items(), key=operator.itemgetter(1), reverse=True
        )
        most_count = sorted_pred_lab[0][1]
        if_right = 0
        most_label = sorted_pred_lab[0][0]
        for pair in sorted_pred_lab:
            if pair[1] < most_count:
                break
            if pair[0] == label:
                if_right = 1
                most_label = pair[0]
        pred = most_label
        correct = if_right
        return pred, correct