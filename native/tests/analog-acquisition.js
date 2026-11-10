function check(condition, message) { if (!condition) throw new Error(message); }
function waitForData(channel, name) {
    for (var i = 0; i < 40; ++i) {
        msleep(100);
        var values = channel.data;
        if (values.length > 0) {
            var finite = 0, lo = Infinity, hi = -Infinity;
            for (var j = 0; j < values.length; ++j) {
                if (isFinite(values[j])) {
                    ++finite; lo = Math.min(lo, values[j]); hi = Math.max(hi, values[j]);
                }
            }
            if (finite > 0) {
                printToConsole(name + " samples=" + values.length + " finite=" + finite + " range=" + lo + "," + hi);
                return values.length;
            }
        }
    }
    throw new Error(name + " produced no finite data");
}
check(launcher.connect("ip:127.0.0.1"), "connect failed");
siggen.enabled = [true, false];
siggen.mode = [1, 1];
siggen.waveform_type = [0, 0];
siggen.waveform_frequency = [1000, 1000];
siggen.waveform_amplitude = [1, 1];
siggen.waveform_offset = [0, 0];
siggen.running = true;
msleep(200);
check(siggen.running, "Signal generator did not start");
osc.channels[0].enabled = true;
osc.time_base = 0.001;
osc.running = true;
check(osc.running, "Oscilloscope did not start");
waitForData(osc.channels[0], "OSC");
osc.running = false;
msleep(100);
spectrum.channels[0].enabled = true;
spectrum.running = true;
check(spectrum.running, "Spectrum analyzer did not start");
waitForData(spectrum.channels[0], "FFT");
spectrum.running = false;
siggen.running = false;
dmm.running = true;
msleep(750);
check(isFinite(dmm.value_ch1) && isFinite(dmm.value_ch2), "Voltmeter returned non-finite values");
printToConsole("DMM " + dmm.value_ch1 + "," + dmm.value_ch2);
dmm.running = false;
launcher.disconnect();
printToConsole("TEST_ANALOG_PASSED");
