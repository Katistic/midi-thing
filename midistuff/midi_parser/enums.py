import enum


class KeySignatureScale(enum.Enum):
    MAJOR = 0
    MINOR = 1


class KeySignatureKey(enum.Enum):
    CF = -7
    GF = -6
    DF = -5
    AF = -4
    EF = -3
    BF = -2
    F = -1
    C = 0
    G = 1
    D = 2
    A = 3
    E = 4
    B = 5
    FS = 6
    CS = 7
