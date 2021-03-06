import theano
import theano.tensor as T


class TestFutureDiv:
    def test_divide_floats(self):
        a = T.dscalar("a")
        b = T.dscalar("b")
        c = theano.function([a, b], b / a)
        d = theano.function([a, b], b // a)
        assert c(6, 3) == 0.5
        assert d(6, 3) == 0.0
