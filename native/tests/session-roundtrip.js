function check(condition, message) { if (!condition) throw new Error(message); }
check(launcher.connect("ip:127.0.0.1"), "connect failed");
osc.time_base = 0.0002;
osc.channels[0].volts_per_div = 0.5;
var expected = osc.time_base;
var expectedVolts = osc.channels[0].volts_per_div;
launcher.save("会话 round trip.ini");
check(fileIO.readAll("会话 round trip.ini").length > 0, "Session file was not written");
osc.time_base = 0.001;
osc.channels[0].volts_per_div = 2;
launcher.load("会话 round trip.ini");
msleep(100);
check(Math.abs(osc.time_base - expected) < 1e-12, "Time base was not restored");
check(Math.abs(osc.channels[0].volts_per_div - expectedVolts) < 1e-12, "Vertical scale was not restored");
launcher.disconnect();
printToConsole("TEST_SESSION_PASSED");
