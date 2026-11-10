function check(condition, message) { if (!condition) throw new Error(message); }
check(!launcher.connect("ip:127.0.0.1:30432"), "A missing service unexpectedly connected");
check(launcher.connect("ip:127.0.0.1"), "Valid connection failed after a failed connection");
launcher.disconnect();
printToConsole("TEST_INVALID_DEVICE_RECOVERY_PASSED");
