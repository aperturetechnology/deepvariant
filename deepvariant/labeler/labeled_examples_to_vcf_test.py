# Copyright 2017 Google Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Tests for deepvariant.labeled_examples_to_vcf."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow import flags
from absl.testing import absltest
from absl.testing import parameterized

from deepvariant.util.io import vcf

from deepvariant import test_utils
from deepvariant.labeler import labeled_examples_to_vcf
from deepvariant.testing import flagsaver

FLAGS = flags.FLAGS


def setUpModule():
  test_utils.init()


class ExamplesToVCFUnitTest(parameterized.TestCase):

  @flagsaver.FlagSaver
  def test_end2end(self):
    FLAGS.ref = test_utils.CHR20_FASTA
    FLAGS.examples = test_utils.GOLDEN_TRAINING_EXAMPLES + '@3'  # Sharded.
    FLAGS.output_vcf = test_utils.test_tmpfile('examples_to_vcf.vcf')

    labeled_examples_to_vcf.main(0)

    self.assertEqual(
        open(FLAGS.output_vcf).readlines(),
        open(test_utils.deepvariant_testdata('golden.training_examples.vcf'))
        .readlines())

  @flagsaver.FlagSaver
  def test_sample_name_flag(self):
    FLAGS.ref = test_utils.CHR20_FASTA
    FLAGS.examples = test_utils.GOLDEN_TRAINING_EXAMPLES
    FLAGS.sample_name = 'sample_name'
    FLAGS.output_vcf = test_utils.test_tmpfile('no_sample_name.vcf')

    labeled_examples_to_vcf.main(0)

    with vcf.VcfReader(FLAGS.output_vcf, use_index=False) as vcf_reader:
      self.assertEqual(list(vcf_reader.header.samples), [FLAGS.sample_name])

  @flagsaver.FlagSaver
  def test_raises_for_unlabeled_examples(self):
    FLAGS.ref = test_utils.CHR20_FASTA
    FLAGS.examples = test_utils.GOLDEN_CALLING_EXAMPLES
    FLAGS.output_vcf = test_utils.test_tmpfile('unlabeled.vcf')

    with self.assertRaisesRegexp(
        ValueError,
        ('Variant .* does not have any genotypes. This tool only works with '
         'variants that have been labeled')):
      labeled_examples_to_vcf.main(0)


if __name__ == '__main__':
  absltest.main()