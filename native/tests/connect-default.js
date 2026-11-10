function check(condition, message) {
    if (!condition) throw new Error(message);
}
printToConsole("TEST_CONNECT_STARTED");
launcher.skip_calibration = false;
check(launcher.connect("ip:127.0.0.1"), "Demo connection failed");
check(typeof osc !== "undefined", "Oscilloscope API missing");
check(typeof spectrum !== "undefined", "Spectrum API missing");
check(typeof siggen !== "undefined", "Signal generator API missing");
check(typeof logic !== "undefined", "Logic analyzer API missing");
check(typeof pattern !== "undefined", "Pattern generator API missing");
check(typeof dio !== "undefined", "Digital IO API missing");
check(typeof dmm !== "undefined", "Voltmeter API missing");
check(typeof network !== "undefined", "Network analyzer API missing");
check(typeof power !== "undefined", "Power supply API missing");
printToConsole("TEST_ALL_NINE_INSTRUMENTS_PRESENT");
launcher.disconnect();
msleep(100);
printToConsole("TEST_CONNECT_PASSED");
