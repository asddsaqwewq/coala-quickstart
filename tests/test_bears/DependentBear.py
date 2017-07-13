from coalib.bears.LocalBear import LocalBear
from tests.test_bears.SpaceConsistencyTestBear import \
    SpaceConsistencyTestBear


class DependentBear(LocalBear):
    BEAR_DEPS = {SpaceConsistencyTestBear}
