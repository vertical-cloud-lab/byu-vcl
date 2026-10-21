# Oct 20 set-up: what was said

Whisper large-v3-turbo on the YouTube audio of each video (`faster-whisper`, int8, VAD on). Gage mostly
works without talking, so this is sparse; times are segment starts, and long silences can make a
segment's start early. MDT is the video time plus the start found in [`alignment.json`](alignment.json).
Side conversations are summarised rather than transcribed. The V3 lines from 14:06 on are from a word-level pass
(`word_timestamps`, VAD threshold 0.3), which recovered *"for these rods"* (the segment pass heard "four") and
*"definitely a leak in here somewhere"*, which the segment pass dropped.

## V1 [`7c8iHQInI_A`](https://youtu.be/7c8iHQInI_A), from 14:35:35 MDT

| Video | MDT | Said |
| --- | --- | --- |
| [0:12](https://youtu.be/7c8iHQInI_A?t=12) | 14:35:47 | Am I going to die in here? |
| [0:23](https://youtu.be/7c8iHQInI_A?t=23) | 14:35:58 | Alright, let's get this first. |
| [0:32](https://youtu.be/7c8iHQInI_A?t=32) | 14:36:07 | Turn on my air pressure. |
| [0:34](https://youtu.be/7c8iHQInI_A?t=34) | 14:36:09 | Might be out of Argon. |
| [1:06](https://youtu.be/7c8iHQInI_A?t=66) | 14:36:41 | I think we're definitely out. |
| [1:36](https://youtu.be/7c8iHQInI_A?t=96) | 14:37:11 | Change that guy. |
| [2:56](https://youtu.be/7c8iHQInI_A?t=176) | 14:38:31 | You ever changed out one of these before? |
| [3:01](https://youtu.be/7c8iHQInI_A?t=181) | 14:38:36 | You ever changed one of these before? |
| [3:03](https://youtu.be/7c8iHQInI_A?t=183) | 14:38:38 | Um, I used to deliver them. |
| [3:05](https://youtu.be/7c8iHQInI_A?t=185) | 14:38:40 | Oh, really? |
| [3:05](https://youtu.be/7c8iHQInI_A?t=185) | 14:38:40 | I can't remember if I'm, I actually supplied them there. |
| [3:08](https://youtu.be/7c8iHQInI_A?t=188) | 14:38:43 | Okay, so for Claude, um, we ran out of Argon tank. |
| [4:41](https://youtu.be/7c8iHQInI_A?t=281) | 14:40:16 | Today is October 20th. |
| [4:43](https://youtu.be/7c8iHQInI_A?t=283) | 14:40:18 | Um, the amount of runs that we did, towards me, it's tighter. |
| [4:56](https://youtu.be/7c8iHQInI_A?t=296) | 14:40:31 | The amount of runs that we did, probably, I don't know how this thing, there we go, that's |
| [5:19](https://youtu.be/7c8iHQInI_A?t=319) | 14:40:54 | it. |
| [5:34](https://youtu.be/7c8iHQInI_A?t=334) | 14:41:09 | There, he said he wanted to bite the hunter there. |
| [5:37](https://youtu.be/7c8iHQInI_A?t=337) | 14:41:12 | Um, it's probably done 10 runs. |
| [5:40](https://youtu.be/7c8iHQInI_A?t=340) | 14:41:15 | I guess around 10 runs for one Argon tank. |
| [5:47](https://youtu.be/7c8iHQInI_A?t=347) | 14:41:22 | Okay, so that's ready to go there. |
| [5:51](https://youtu.be/7c8iHQInI_A?t=351) | 14:41:26 | I'll put this back. |
| [6:25](https://youtu.be/7c8iHQInI_A?t=385) | 14:42:00 | That's good. |
| [6:27](https://youtu.be/7c8iHQInI_A?t=387) | 14:42:02 | I'm going to make sure that this is, it can work for us. |
| [6:43](https://youtu.be/7c8iHQInI_A?t=403) | 14:42:18 | Looks good to me. |
| [6:51](https://youtu.be/7c8iHQInI_A?t=411) | 14:42:26 | Looks like there's some aluminum down at the bottom of that thing. |
| [6:59](https://youtu.be/7c8iHQInI_A?t=419) | 14:42:34 | Tweezers. |
| [6:59](https://youtu.be/7c8iHQInI_A?t=419) | 14:42:34 | I don't know if I can get this, I don't think this is going to work. |
| [7:03](https://youtu.be/7c8iHQInI_A?t=423) | 14:42:38 | I'm going to have to, yeah. |
| [8:07](https://youtu.be/7c8iHQInI_A?t=487) | 14:43:42 | (side conversation about the powder doser, not set-up) |
| [9:16](https://youtu.be/7c8iHQInI_A?t=556) | 14:44:51 | Yeah, that looks right. |
| [11:19](https://youtu.be/7c8iHQInI_A?t=679) | 14:46:54 | Oops. |
| [11:20](https://youtu.be/7c8iHQInI_A?t=680) | 14:46:55 | Well, that's kind of stuck for now, I guess. |
| [12:49](https://youtu.be/7c8iHQInI_A?t=769) | 14:48:24 | It's none of a big deal. |
| [12:53](https://youtu.be/7c8iHQInI_A?t=773) | 14:48:28 | We'll get it out eventually when we need to. |
| [14:44](https://youtu.be/7c8iHQInI_A?t=884) | 14:50:19 | Off. |
| [14:46](https://youtu.be/7c8iHQInI_A?t=886) | 14:50:21 | 17, let's see if this is right. |
| [14:49](https://youtu.be/7c8iHQInI_A?t=889) | 14:50:24 | Okay, that's going to fit there. |
| [14:51](https://youtu.be/7c8iHQInI_A?t=891) | 14:50:26 | This new system. |
| [17:50](https://youtu.be/7c8iHQInI_A?t=1070) | 14:53:25 | Looks like it's a little heavy right now. |
| [17:57](https://youtu.be/7c8iHQInI_A?t=1077) | 14:53:32 | All right. |
| [17:59](https://youtu.be/7c8iHQInI_A?t=1079) | 14:53:34 | And on. |
| [22:08](https://youtu.be/7c8iHQInI_A?t=1328) | 14:57:43 | I have to. |
| [22:17](https://youtu.be/7c8iHQInI_A?t=1337) | 14:57:52 | Off. |

## V2 [`vPhZTvfIu7s`](https://youtu.be/vPhZTvfIu7s), from 15:02:16 MDT

| Video | MDT | Said |
| --- | --- | --- |
| [0:02](https://youtu.be/vPhZTvfIu7s?t=2) | 15:02:18 | All right, I've got 45 minutes worth of video time to finish this, so I've got the speed to 60. |
| [4:03](https://youtu.be/vPhZTvfIu7s?t=243) | 15:06:19 | That's not supposed to go that way. |
| [9:26](https://youtu.be/vPhZTvfIu7s?t=566) | 15:11:42 | You know what's not good is when you discover a seal. |
| [9:30](https://youtu.be/vPhZTvfIu7s?t=570) | 15:11:46 | It's supposed to be inside this after you put it together. |
| [9:34](https://youtu.be/vPhZTvfIu7s?t=574) | 15:11:50 | Oh, that'll work. |
| [9:35](https://youtu.be/vPhZTvfIu7s?t=575) | 15:11:51 | Yeah. |
| [9:37](https://youtu.be/vPhZTvfIu7s?t=577) | 15:11:53 | Bro! |
| [9:40](https://youtu.be/vPhZTvfIu7s?t=580) | 15:11:56 | This is the system that converts the digital ultrasonic signal to physical vibrations. |
| [9:49](https://youtu.be/vPhZTvfIu7s?t=589) | 15:12:05 | Oh my gosh, I don't believe it. |
| [10:06](https://youtu.be/vPhZTvfIu7s?t=606) | 15:12:22 | It's not true. |
| [10:08](https://youtu.be/vPhZTvfIu7s?t=608) | 15:12:24 | (side conversation about clumps blocking the powder doser's outlet, not set-up) |
| [10:42](https://youtu.be/vPhZTvfIu7s?t=642) | 15:12:58 | Hey Wesley, how are you? |
| [14:06](https://youtu.be/vPhZTvfIu7s?t=846) | 15:16:22 | Pretty good, thanks. |

## V3 [`OFS_PLxoV94`](https://youtu.be/OFS_PLxoV94), from 15:19:50 MDT

| Video | MDT | Said |
| --- | --- | --- |
| [3:18](https://youtu.be/OFS_PLxoV94?t=198) | 15:23:08 | (side conversation about mixing powders in the melt, not set-up) |
| [14:06](https://youtu.be/OFS_PLxoV94?t=846) | 15:33:56 | This one is cracking. I think that means we should get a new one. (Time from a word-level pass; the VAD pass ran this into one long segment starting at 11:34.) |
| [15:42](https://youtu.be/OFS_PLxoV94?t=942) | 15:35:32 | No, you're good. |
| [17:08](https://youtu.be/OFS_PLxoV94?t=1028) | 15:36:58 | I think we're ready for these rods |
| [19:37](https://youtu.be/OFS_PLxoV94?t=1177) | 15:39:27 | to do this thing. |
| [23:58](https://youtu.be/OFS_PLxoV94?t=1438) | 15:43:49 | Definitely a leak in here somewhere. |

## V4 [`Ev9WMscAetw`](https://youtu.be/Ev9WMscAetw), from 15:48:09 MDT

| Video | MDT | Said |
| --- | --- | --- |
| [1:53](https://youtu.be/Ev9WMscAetw?t=113) | 15:50:02 | Do you know which jar it's from? |
| [1:55](https://youtu.be/Ev9WMscAetw?t=115) | 15:50:04 | What's that? |
| [2:00](https://youtu.be/Ev9WMscAetw?t=120) | 15:50:09 | Yeah, I guess in the t-shirt we should just keep track of which jar it comes from and we can just put it right back in. |
| [2:11](https://youtu.be/Ev9WMscAetw?t=131) | 15:50:20 | But if you need something you can use this guy. |
| [2:14](https://youtu.be/Ev9WMscAetw?t=134) | 15:50:23 | All 40-47? |
| [2:16](https://youtu.be/Ev9WMscAetw?t=136) | 15:50:25 | Yeah, I believe most of them are. It says exactly on it if it is or not. |
| [2:21](https://youtu.be/Ev9WMscAetw?t=141) | 15:50:30 | That'd just be about right. Sheesh! |
