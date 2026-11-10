function check(condition, message) { if (!condition) throw new Error(message); }
for (var i = 0; i < 12; ++i) {
    check(launcher.connect("ip:127.0.0.1"), "Connection failed on cycle " + i);
    check(typeof osc !== "undefined" && typeof logic !== "undefined", "Missing instrument on cycle " + i);
    launcher.disconnect();
    msleep(50);
    printToConsole("RECONNECT_CYCLE " + (i + 1));
}
printToConsole("TEST_RECONNECT_PASSED");
