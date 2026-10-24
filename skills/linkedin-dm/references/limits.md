# LinkedIn limits we rely on

Checked 2026-10-23. LinkedIn changes these without notice, and it does not publish the
"see more" cutoff at all. When a number matters, check it in LinkedIn's own editor, which
wins over anything here. Recheck this file every few months.

## Before "see more" in the feed (observed, not published)

| view | what shows | sources |
| --- | --- | --- |
| mobile, text only | about 3 lines, about 140 characters | [1], [2], [3], [4] |
| desktop, text only | about 5 lines, about 210 characters | [1], [2], [3], [4] |
| post with image, video or document | about 3 lines on both | [1] |

A line break counts as a full line, and a blank line between paragraphs uses one of the
three mobile lines [1]. One source says the cutoff "varies by device" and is not
documented [5]. So treat these as a safe target, not a promise: keep the hook inside the
first line and under about 140 characters.

## Field limits

| field | limit | sources |
| --- | --- | --- |
| post | 3,000 characters | [2], [5] |
| comment | 1,250 characters (one source reports up to 1,750) | [3], [5] |
| headline | 220 characters, about 60 to 70 show in search | [2], [3] |
| About | 2,600 characters, about 300 show before "see more" | [2], [3] |
| invitation note | 200 characters (it was 300 before) | [8] |
| personalized invitation notes, free account | 3 a month (an older LinkedIn page says 5); Premium has no monthly cap | [8], [9] |
| document post (PDF, PPT, DOC) | 100 MB, 300 pages | [6] |

## Invitations

LinkedIn does not publish a weekly invite number. It restricts accounts that send many
invitations in a short time, or whose invitations are often ignored or marked as spam [7].
A restriction usually lasts about a week, and LinkedIn support can't lift or shorten it [9].
Vendors observe a ceiling of about 100 invitations a week for most accounts [7]. Our tools
default to 5 a day and stop at 50 a week, well under that ceiling.

## Sources

1. linkedinpreview.com, "LinkedIn Hook Preview", 2026-05-04. https://linkedinpreview.com/blog/linkedin-hook-preview
2. Eden, "LinkedIn character limits in 2026", 2026-08-21. https://eden.so/blog/linkedin-character-limits/
3. AuthoredUp, "LinkedIn character limit", updated 2026-08-11. https://authoredup.com/blog/linkedin-character-limit
4. Hublead, "LinkedIn Character Limits 2026", LinkedIn Help pages checked 2026-09-19. https://www.hublead.io/linkedin-character-limit
5. ContentIn, "LinkedIn post character limit", updated 2026-10-22. https://contentin.io/blog/linkedin-post-character-limit/
6. Ayrshare, LinkedIn media guidelines. https://www.ayrshare.com/docs/media-guidelines/linkedin.md (LinkedIn's own page, https://www.linkedin.com/help/linkedin/answer/97459, blocks automated reading; check it by hand)
7. Hublead, "LinkedIn Invitation Limit 2026", citing LinkedIn Help a551012 and a550555, checked 2026-09-19. https://www.hublead.io/linkedin-invitation-limit

8. LinkedIn Help, "Personalize invitations to connect", read by hand in a browser 2026-10-24
   (page last updated about 6 months earlier). https://www.linkedin.com/help/linkedin/answer/46662
   Says: personal notes on up to three requests a month on free accounts, up to 200 characters each.
9. LinkedIn Help, "Invitation limit reached", read by hand 2026-10-24. https://www.linkedin.com/help/billing/answer/a550555
   Says: all members have invitation limits; hitting one usually means a restriction of about one
   week that support can't lift; free members can personalize five requests a month (older page).

Sources 1 to 7 are third-party pages. LinkedIn Help blocks automated reading, so 8 and 9 were
read by hand in a browser. LinkedIn still publishes no weekly invite number.
