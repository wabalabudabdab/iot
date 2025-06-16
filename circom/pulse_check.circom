pragma circom 2.0.0;

template PulseCheck() {
    signal input pulse;
    signal input threshold;
    signal input alert;

    signal diff;
    diff <== pulse - threshold;

    signal prod;
    prod <== alert * diff;
    prod === diff;

    signal output result;
    result <== prod;
}

component main = PulseCheck();
