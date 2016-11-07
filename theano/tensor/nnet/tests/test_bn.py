from __future__ import absolute_import, print_function, division
import theano
import theano.tensor as T
from theano.tests import unittest_tools as utt
import numpy

from theano.tensor.nnet import bn


def test_BNComposite():
    try:
        orig = theano.config.compute_test_value

        theano.config.compute_test_value = 'raise'

        def bn_ref(x, G, B, M, V):
            n = (x - M) / V
            return n * G + B

        numpy.random.seed(1234)
        X = 1 + numpy.random.random([10, 20]).astype('float32')
        B = 1 + numpy.random.random([20]).astype('float32')
        G = 1 + numpy.random.random([20]).astype('float32')
        M = 1 + numpy.random.random([20]).astype('float32')
        V = 1 + numpy.random.random([20]).astype('float32')

        x = theano.tensor.matrix('x')
        b = theano.tensor.vector('b')
        g = theano.tensor.vector('g')
        m = theano.tensor.vector('m')
        v = theano.tensor.vector('v')

        x.tag.test_value = numpy.random.rand(2, 2).astype(theano.config.floatX)
        b.tag.test_value = numpy.random.rand(2).astype(theano.config.floatX)
        g.tag.test_value = numpy.random.rand(2).astype(theano.config.floatX)
        m.tag.test_value = numpy.random.rand(2).astype(theano.config.floatX)
        v.tag.test_value = numpy.random.rand(2).astype(theano.config.floatX)

        bn_ref_op = bn_ref(x, g, b, m, v)
        f_ref = theano.function([x, b, g, m, v], [bn_ref_op])
        res_ref = f_ref(X, G, B, M, V)
        for mode in ['low_mem', 'high_mem']:
            bn_op = bn.batch_normalization(x, g, b, m, v, mode=mode)
            f = theano.function([x, b, g, m, v], [bn_op])
            res = f(X, G, B, M, V)
            utt.assert_allclose(res_ref, res)
    finally:
        theano.config.compute_test_value = orig


def test_batch_normalization():

    def bn_ref(x, G, B, M, V):
        n = (x - M) / V
        return n * G + B

    numpy.random.seed(1234)
    X = 1 + numpy.random.random([10, 20]).astype('float32')
    B = 1 + numpy.random.random([20]).astype('float32')
    G = 1 + numpy.random.random([20]).astype('float32')
    M = 1 + numpy.random.random([20]).astype('float32')
    V = 1 + numpy.random.random([20]).astype('float32')

    x = theano.tensor.matrix('x')
    b = theano.tensor.vector('b')
    g = theano.tensor.vector('g')
    m = theano.tensor.vector('m')
    v = theano.tensor.vector('v')

    bn_ref_op = bn_ref(x, g, b, m, v)
    f_ref = theano.function([x, b, g, m, v], [bn_ref_op])
    res_ref = f_ref(X, G, B, M, V)
    for mode in ['low_mem', 'high_mem']:
        bn_op = bn.batch_normalization(x, g, b, m, v, mode=mode)
        f = theano.function([x, b, g, m, v], [bn_op])
        res = f(X, G, B, M, V)
        utt.assert_allclose(res_ref, res)

        def bn_f(inputs, gamma, beta, mean, std):
            return bn.batch_normalization(inputs, gamma, beta, mean, std, mode=mode)
        utt.verify_grad(bn_f, [X, G, B, M, V])

    bn_ref_op = bn_ref(x, g, b, x.mean(axis=0, keepdims=True), x.std(axis=0, keepdims=True))
    f_ref = theano.function([x, b, g], [bn_ref_op])
    res_ref = f_ref(X, G, B)
    for mode in ['low_mem', 'high_mem']:
        bn_op = bn.batch_normalization(x, g, b, x.mean(axis=0, keepdims=True), x.std(axis=0, keepdims=True), mode=mode)
        f = theano.function([x, b, g], [bn_op])
        res = f(X, G, B)
        utt.assert_allclose(res_ref, res)

        def bn_f(inputs, gamma, beta, mean, std):
            return bn.batch_normalization(inputs, gamma, beta, mean, std, mode=mode)
        utt.verify_grad(bn_f, [X, G, B,
                               X.mean(axis=0)[numpy.newaxis], X.std(axis=0)[numpy.newaxis]])


def test_bn_feature_maps():

    def bn_ref(x, G, B, M, V):
        n = (x - M) / V
        return n * G + B

    numpy.random.seed(1234)
    X = 1 + numpy.random.random([2, 3, 4, 4]).astype('float32')
    B = 1 + numpy.random.random([3]).astype('float32')
    G = 1 + numpy.random.random([3]).astype('float32')
    M = 1 + numpy.random.random([3]).astype('float32')
    V = 1 + numpy.random.random([3]).astype('float32')

    x = theano.tensor.tensor4('x')
    b = theano.tensor.vector('b')
    g = theano.tensor.vector('g')
    m = theano.tensor.vector('m')
    v = theano.tensor.vector('v')

    bn_ref_op = bn_ref(x,
                       g.dimshuffle('x', 0, 'x', 'x'),
                       b.dimshuffle('x', 0, 'x', 'x'),
                       m.dimshuffle('x', 0, 'x', 'x'),
                       v.dimshuffle('x', 0, 'x', 'x'))
    f_ref = theano.function([x, b, g, m, v], [bn_ref_op])
    res_ref = f_ref(X, G, B, M, V)

    for mode in ['low_mem', 'high_mem']:
        bn_op = bn.batch_normalization(x,
                                       g.dimshuffle('x', 0, 'x', 'x'),
                                       b.dimshuffle('x', 0, 'x', 'x'),
                                       m.dimshuffle('x', 0, 'x', 'x'),
                                       v.dimshuffle('x', 0, 'x', 'x'),
                                       mode=mode)
        f = theano.function([x, b, g, m, v], [bn_op])
        res = f(X, G, B, M, V)
        utt.assert_allclose(res_ref, res)

        def conv_bn(inputs, gamma, beta, mean, std):
            return bn.batch_normalization(inputs,
                                          gamma.dimshuffle('x', 0, 'x', 'x'),
                                          beta.dimshuffle('x', 0, 'x', 'x'),
                                          mean.dimshuffle('x', 0, 'x', 'x'),
                                          std.dimshuffle('x', 0, 'x', 'x'),
                                          mode=mode)
        utt.verify_grad(conv_bn, [X, G, B, M, V])


def test_batch_normalization_train():
    utt.seed_rng()

    for axes in ('per-activation', 'spatial', (1, 2, 3, 4)):
        for vartype in (T.tensor5, T.tensor4, T.tensor3, T.matrix, T.vector):
            x, scale, bias = (vartype(n) for n in ('x', 'scale', 'bias'))
            ndim = x.ndim
            eps = 5e-3  # some non-standard value to test if it's used

            # remove non-existing axes
            if isinstance(axes, tuple):
                axes = tuple(i for i in axes if i < ndim)
            if len(axes) == 0:
                continue

            # forward pass
            out, x_mean, x_invstd = bn.batch_normalization_train(
                x, scale, bias, axes, eps)
            # reference forward pass
            if axes == 'per-activation':
                axes2 = (0,)
            elif axes == 'spatial':
                axes2 = (0,) + tuple(range(2, ndim))
            else:
                axes2 = axes
            x_mean2 = x.mean(axis=axes2, keepdims=True)
            x_invstd2 = T.inv(T.sqrt(x.var(axis=axes2, keepdims=True) + eps))
            scale2 = T.addbroadcast(scale, *axes2)
            bias2 = T.addbroadcast(bias, *axes2)
            out2 = (x - x_mean2) * (scale2 * x_invstd2) + bias2
            # backward pass
            dy = vartype('dy')
            grads = T.grad(None, wrt=[x, scale, bias], known_grads={out: dy})
            # reference backward pass
            grads2 = T.grad(None, wrt=[x, scale, bias], known_grads={out2: dy})
            # compile
            f = theano.function([x, scale, bias, dy],
                                [out, x_mean, x_invstd, out2, x_mean2, x_invstd2] +
                                grads + grads2, mode='FAST_RUN')
            # check if the abstract Ops have been replaced
            assert not any([isinstance(n.op, (bn.AbstractBatchNormTrain,
                                              bn.AbstractBatchNormInference,
                                              bn.AbstractBatchNormTrainGrad))
                            for n in f.maker.fgraph.toposort()])
            # run
            for data_shape in ((5, 10, 30, 40, 10), (4, 3, 1, 1, 1), (1, 1, 5, 5, 5)):
                data_shape = data_shape[:ndim]
                param_shape = tuple(1 if d in axes2 else s
                                    for d, s in enumerate(data_shape))
                X = 4 + 3 * numpy.random.randn(*data_shape).astype(theano.config.floatX)
                Dy = -1 + 2 * numpy.random.randn(*data_shape).astype(theano.config.floatX)
                Scale = numpy.random.randn(*param_shape).astype(theano.config.floatX)
                Bias = numpy.random.randn(*param_shape).astype(theano.config.floatX)
                outputs = f(X, Scale, Bias, Dy)
                # compare outputs
                utt.assert_allclose(outputs[0], outputs[0 + 3])  # out
                utt.assert_allclose(outputs[1], outputs[1 + 3])  # mean
                utt.assert_allclose(outputs[2], outputs[2 + 3])  # invstd
                # compare gradients
                utt.assert_allclose(outputs[6], outputs[6 + 3], atol=1e-4)  # dx
                utt.assert_allclose(outputs[7], outputs[7 + 3], rtol=2e-4, atol=1e-4)  # dscale
                utt.assert_allclose(outputs[8], outputs[8 + 3])  # dbias


def test_batch_normalization_test():
    for axes in ('per-activation', 'spatial', (1, 2, 3, 4)):
        for vartype in (T.tensor5, T.tensor4, T.tensor3, T.matrix, T.vector):
            x, scale, bias, mean, var = (vartype(n)
                                         for n in ('x', 'scale', 'bias', 'mean', 'var'))
            ndim = x.ndim
            eps = 5e-3  # some non-standard value to test if it's used

            # remove non-existing axes
            if isinstance(axes, tuple):
                axes = tuple(i for i in axes if i < ndim)
            if len(axes) == 0:
                continue

            # forward pass
            out = bn.batch_normalization_test(x, scale, bias, mean,
                                              var, axes, eps)
            # reference forward pass
            if axes == 'per-activation':
                axes2 = (0,)
            elif axes == 'spatial':
                axes2 = (0,) + tuple(range(2, ndim))
            else:
                axes2 = axes
            scale2, bias2, mean2, var2 = (T.addbroadcast(t, *axes2)
                                          for t in (scale, bias, mean, var))
            out2 = (x - mean2) * (scale2 / T.sqrt(var2 + eps)) + bias2
            # backward pass
            dy = vartype('dy')
            grads = T.grad(None, wrt=[x, scale, bias, mean, var], known_grads={out: dy})
            # reference backward pass
            grads2 = T.grad(None, wrt=[x, scale, bias, mean, var], known_grads={out2: dy})
            # compile
            f = theano.function([x, scale, bias, mean, var, dy],
                                [out, out2] + grads + grads2, mode='FAST_RUN')
            # check if the abstract Ops have been replaced
            assert not any([isinstance(n.op, (bn.AbstractBatchNormTrain,
                                              bn.AbstractBatchNormInference,
                                              bn.AbstractBatchNormTrainGrad))
                            for n in f.maker.fgraph.toposort()])
            # run
            for data_shape in ((10, 20, 30, 40, 10), (4, 3, 1, 1, 1), (1, 1, 5, 5, 5)):
                data_shape = data_shape[:ndim]
                param_shape = tuple(1 if d in axes2 else s
                                    for d, s in enumerate(data_shape))
                X = 4 + 3 * numpy.random.randn(*data_shape).astype(theano.config.floatX)
                Dy = -1 + 2 * numpy.random.randn(*data_shape).astype(theano.config.floatX)
                Scale = numpy.random.randn(*param_shape).astype(theano.config.floatX)
                Bias = numpy.random.randn(*param_shape).astype(theano.config.floatX)
                Mean = numpy.random.randn(*param_shape).astype(theano.config.floatX)
                Var = numpy.random.rand(*param_shape).astype(theano.config.floatX)
                outputs = f(X, Scale, Bias, Mean, Var, Dy)
                # compare outputs
                utt.assert_allclose(outputs[0], outputs[1])  # out
                # compare gradients
                utt.assert_allclose(outputs[2], outputs[2 + 5], atol=4e-5)  # dx
                utt.assert_allclose(outputs[3], outputs[3 + 5], atol=4e-5)  # dscale
                utt.assert_allclose(outputs[4], outputs[4 + 5])  # dbias
                utt.assert_allclose(outputs[5], outputs[5 + 5])  # dmean
                utt.assert_allclose(outputs[6], outputs[6 + 5], rtol=2e-3, atol=4e-5)  # dvar
