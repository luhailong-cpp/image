# 03 production contract (2026-09-30)

Only this role directory may be written. Reference authority: S/front and original source/idle-v1/prompt.txt: anatomical RIGHT hand lotus lantern, LEFT jade flask, LEFT hair flower. Old E has incorrect hand/ornament depth; do not reproduce it. In E near RIGHT arm/leg, far LEFT; flower far hidden. E master run01 = generation/E/01-v3.png. Do not copy/mirror/interpolate poses. One builtin image_gen call per single native >=1024 square frame. Actual returned model and quality unknown/null, configured target from shared JSON. Actual refs include designs/jubaozhai-ui/02-characters.png every call. Preserve fixed E master canvas size, body/face/prop dimensions and registration. Small physical vertical body motion is required. No per-frame bbox fitting or lowest-foot alignment.

Cycle 16x30ms=480ms. E phases:
01 right contact ahead; left folded rear. Right lantern arm back, left flask arm front.
02 right loading compression; left foot swings forward from rear.
03 right midsupport under pelvis; left knee/foot passes bent behind near thigh.
04 right late support toe behind; left knee rises in front.
05 right toeoff behind; left knee forward; right lantern arm forward, left flask arm back.
06 early flight, both feet clear; right heel folded back, left knee unfolding ahead.
07 flight apex, left extends forward, right folded rear; head ~25px higher in 1024 coordinates than contact.
08 late flight, left reaches floor almost landing, right folded rear.
09 left contact ahead; right folded rear. Right lantern arm front, left flask arm back.
10 left loading compression; right foot begins swing from rear.
11 left midsupport under pelvis; right knee passes bent in front of far support thigh.
12 left late support toe behind; right knee rises ahead.
13 left toeoff behind; right knee forward; right lantern arm back, left flask arm front.
14 early flight, both feet clear; left heel folded rear, right knee unfolding ahead.
15 flight apex, right extends forward, left folded rear; head ~25px above contact.
16 late flight, right reaches floor almost landing, left folded rear. Seam to01.

Record each invocation prompt/job/native image/.generation.json using tools/record_generation.py. Job schema: {output, prompt, references:[{path,purpose}],status optional,review optional}. All paths output/prompt relative role. Script CLI python tools/record_generation.py <absolute-job-file> <host-output.png>. Runtime C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe. References viewed before call. Never mark dynamic acceptance from static keyframes.

