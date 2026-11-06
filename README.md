<div align="center">

<img src="receipt/receipt.svg" width="476" alt="An animated thermal receipt printing out of a small printer. It lists my hackathon projects as line items, my live GitHub stats as totals, a QR code to my portfolio, a VERIFIED stamp, and the SHA-256 hash of the data it was printed from.">

</div>

### Every number on that receipt is real. Check it.

A [GitHub Action](.github/workflows/receipt.yml) reprints the receipt every day from the GitHub API. It saves the raw numbers to [`receipt/data.json`](receipt/data.json) and prints that file's SHA-256 at the bottom of the receipt. To check that the two match:

```sh
curl -s https://raw.githubusercontent.com/Ritesh-Root/Ritesh-Root/main/receipt/data.json | sha256sum
```

If the hashes don't match, the receipt is wrong. If they're only out of sync for a few minutes, that's GitHub's image cache.

### Hi, I'm Ritesh 👋

I'm a BTech CSE student who builds at hackathons, mostly AI agents that have to show their work. The common thread: an AI shouldn't get to say *"done"* unless it has a receipt to back it up, like a signed check, a hash-chained log, a quote from the source, or a human approval.

### Itemised

| | Project | What it does |
|---|---|---|
| 🧾 | [**switch-notary**](https://github.com/Ritesh-Root/switch-notary) | Checks every claim AI coworkers make against git, its own test re-run and the tool log, then issues a signed receipt. Rust. |
| 🏥 | [**aarogya-vayu**](https://github.com/Ritesh-Root/aarogya-vayu) · [live](https://aarogya-vayu.vercel.app) | Moves medicine to rural clinics before smog or heat empties their shelves. Hash-chained audit log, a doctor approves every transfer. **Top 10, Google Code for Communities.** |
| 🍽️ | [**agora-taste-council**](https://github.com/Ritesh-Root/agora-taste-council) · [live](https://agora-plus-295478535981.us-central1.run.app) | Picks what the whole family will enjoy. Qloo's taste graph + maximin, so nobody is left out. |
| 🧮 | [**taxeasy**](https://github.com/Ritesh-Root/taxeasy) | A CA on WhatsApp for Indian small businesses: GST, bills, tax. |
| 🔬 | [**neural-lens**](https://github.com/Ritesh-Root/neural-lens) | Six hands-on x-ray labs that show what goes on inside an AI. |
| 🕯️ | [**ofrenda**](https://github.com/Ritesh-Root/ofrenda) | An altar that answers only with what your family remembers, and keeps both versions when they disagree. |
| 👆 | [**pulsepay-paypal**](https://github.com/Ritesh-Root/pulsepay-paypal) | Pay at any shop with a fingerprint or face plus a PIN. |
| ⏸️ | [**hold**](https://github.com/Ritesh-Root/hold) | A household agent that shows the plan, waits, then does it. Rust + MCP. |

### Find me

[![Portfolio](https://img.shields.io/badge/riteshhoon.online-111?logo=googlechrome&logoColor=white)](https://riteshhoon.online) [![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/riteshhoon) [![X](https://img.shields.io/badge/X-black.svg?logo=X&logoColor=white)](https://x.com/riteshhoon) [![Instagram](https://img.shields.io/badge/Instagram-%23E4405F.svg?logo=Instagram&logoColor=white)](https://instagram.com/riteshhoon) [![Reddit](https://img.shields.io/badge/Reddit-%23FF4500.svg?logo=Reddit&logoColor=white)](https://reddit.com/user/riteshhoon) [![Discord](https://img.shields.io/badge/Discord-%237289DA.svg?logo=discord&logoColor=white)](https://discord.gg/3BNhUEtZ) [![Codepen](https://img.shields.io/badge/Codepen-000000?logo=codepen&logoColor=white)](https://codepen.io/Ritesh-Mahato) [![Email](https://img.shields.io/badge/Email-D14836?logo=gmail&logoColor=white)](mailto:riteshmahatowork@gmail.com)

<details>
<summary><b>The full tool shelf</b></summary>
<br>

![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Rust](https://img.shields.io/badge/rust-%23000000.svg?style=for-the-badge&logo=rust&logoColor=white) ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) ![Go](https://img.shields.io/badge/go-%2300ADD8.svg?style=for-the-badge&logo=go&logoColor=white) ![Java](https://img.shields.io/badge/java-%23ED8B00.svg?style=for-the-badge&logo=openjdk&logoColor=white) ![C](https://img.shields.io/badge/c-%2300599C.svg?style=for-the-badge&logo=c&logoColor=white) ![C++](https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white) ![Solidity](https://img.shields.io/badge/Solidity-%23363636.svg?style=for-the-badge&logo=solidity&logoColor=white) ![Bash Script](https://img.shields.io/badge/bash_script-%23121011.svg?style=for-the-badge&logo=gnu-bash&logoColor=white) ![PowerShell](https://img.shields.io/badge/PowerShell-%235391FE.svg?style=for-the-badge&logo=powershell&logoColor=white) ![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white) ![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white) ![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white) ![Cloudflare](https://img.shields.io/badge/Cloudflare-F38020?style=for-the-badge&logo=Cloudflare&logoColor=white) ![Vercel](https://img.shields.io/badge/vercel-%23000000.svg?style=for-the-badge&logo=vercel&logoColor=white) ![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white) ![MySQL](https://img.shields.io/badge/mysql-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white) ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white) ![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white) ![TensorFlow](https://img.shields.io/badge/TensorFlow-%23FF6F00.svg?style=for-the-badge&logo=TensorFlow&logoColor=white) ![Figma](https://img.shields.io/badge/figma-%23F24E1E.svg?style=for-the-badge&logo=figma&logoColor=white) ![Adobe](https://img.shields.io/badge/adobe-%23FF0000.svg?style=for-the-badge&logo=adobe&logoColor=white) ![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white) ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) ![Arduino](https://img.shields.io/badge/-Arduino-00979D?style=for-the-badge&logo=Arduino&logoColor=white) ![Windows Terminal](https://img.shields.io/badge/Windows%20Terminal-%234D4D4D.svg?style=for-the-badge&logo=windows-terminal&logoColor=white) ![Epic Games](https://img.shields.io/badge/epicgames-%23313131.svg?style=for-the-badge&logo=epicgames&logoColor=white)

</details>

<sub>Want to change what's on the receipt? The line items are in [`receipt/items.json`](receipt/items.json), and the printer is [`scripts/build_receipt.py`](scripts/build_receipt.py) (Python standard library only).</sub>
