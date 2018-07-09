#!/usr/bin/env python3

#
#  Copyright 2016 Peter de Vocht
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import numpy as np
from sklearn.decomposition import PCA
from typing import List


class Word:
    """An embedding word with associated vector"""

    def __init__(self, text, vector):
        self.text = text
        self.vector = vector


class Sentence:
    """A sentence, a list of words"""

    def __init__(self, word_list):
        self.word_list = word_list

    # return the length of a sentence
    def len(self) -> int:
        return len(self.word_list)


def get_word_frequency(word_text):
    """todo: get the frequency for a word in a document set"""
    return 1.0


def sentence_to_vec(
    sentence_list: List[Sentence], embedding_size: int, a: float = 1e-3, debug=False
):
    """
    Convert a list of sentence with word2vec items into a set of sentence vectors

    A SIMPLE BUT TOUGH TO BEAT BASELINE FOR SENTENCE EMBEDDINGS
    Sanjeev Arora, Yingyu Liang, Tengyu Ma
    Princeton University
    """
    if debug:
        print("[DEBUG] sentence_to_vec")
    sentence_set = []
    for i, sentence in enumerate(sentence_list):
        if debug:
            print(f"Progress: {i}/{len(sentence_list)}", end="\r")
        vs = np.zeros(
            embedding_size
        )  # add all word2vec values into one vector for the sentence
        sentence_length = sentence.len()
        for word in sentence.word_list:
            a_value = a / (
                a + get_word_frequency(word.text)
            )  # smooth inverse frequency, SIF
            vs = np.add(
                vs, np.multiply(a_value, word.vector)
            )  # vs += sif * word_vector
        vs = np.divide(vs, sentence_length)  # weighted average
        sentence_set.append(vs)  # add to our existing re-calculated set of sentences

    sentence_set = np.array(sentence_set)
    sentence_set = np.nan_to_num(sentence_set)

    if debug:
        print()

    # calculate PCA of this sentence set
    if debug:
        print("[DEBUG] Compution PCA (1/3)")

    pca = PCA(n_components=embedding_size)
    pca.fit(np.array(sentence_set))
    u = pca.components_[0]  # the PCA vector
    u = np.multiply(u, np.transpose(u))  # u x uT

    # pad the vector?  (occurs if we have less sentences than embeddings_size)
    if debug:
        print("[DEBUG] Padding vector (2/3)")

    if len(u) < embedding_size:
        for _ in range(embedding_size - len(u)):
            u = np.append(u, 0)  # add needed extension for multiplication below

    if debug:
        print("[DEBUG] Building final vectors (3/3)")

    # resulting sentence vectors, vs = vs -u x uT x vs
    sentence_vecs = sentence_set - (u * sentence_set)
    return sentence_vecs
