function check(condition, message) { if (!condition) throw new Error(message); }
check(launcher.connect("ip:127.0.0.1"), "connect failed");
network.min_freq = 1000;
network.max_freq = 10000;
network.samples_count = 10;
network.averaging = 1;
network.periods = 1;
network.running = true;
// The public running property selects continuous sweeps, not single-shot mode.
for (var i = 0; i < 100; ++i) {
    msleep(100);
    var progress = network.freq;
    if (progress.length >= 10 && progress[progress.length - 1] >= 9990) break;
}
network.running = false;
check(!network.running, "Network sweep could not be stopped");
var frequency = network.freq;
var magnitude = network.data;
var phase = network.phase;
printToConsole("NETWORK_FREQUENCY " + JSON.stringify(frequency));
check(frequency.length >= 10 && magnitude.length === frequency.length, "Incomplete sweep arrays");
check(phase.length === frequency.length, "Incomplete phase array");
for (var j = 0; j < frequency.length; ++j) {
    check(isFinite(frequency[j]) && isFinite(magnitude[j]), "Non-finite network measurement");
    check(isFinite(phase[j]) && Math.abs(phase[j]) <= 360, "Invalid phase measurement");
    if (j > 0) check(frequency[j] > frequency[j - 1], "Sweep frequency is not increasing");
}
printToConsole("NETWORK points=" + frequency.length + " range=" + frequency[0] + "," + frequency[frequency.length - 1]);
launcher.disconnect();
printToConsole("TEST_NETWORK_PASSED");
