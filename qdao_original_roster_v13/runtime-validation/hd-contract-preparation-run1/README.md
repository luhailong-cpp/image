# HD contract preparation Run 1

This is a failed compile preparation run, not acceptance. Unity exited 1 because the expanded sandbox assertion used `Is.AnyOf`, which this project's NUnit does not provide. No EditMode or PlayMode tests ran. The original input snapshot and log are preserved.

The formal source correction uses `Is.EqualTo(13).Or.EqualTo(14)`; a new combined run will include that correction and the completed bounded HD animator/battle cache. This run contains no HD artwork; it cannot demonstrate HD visual quality or HD runtime loading.

The full input comparison contains three added and four changed C# files, and no art resource changes.
