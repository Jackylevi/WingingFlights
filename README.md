# NYC to Europe Flight Deal Finder

This Python script hunts for cheap roundtrip flights from NYC (JFK, LGA, EWR) to major European cities, keeping it under $350 for trips between 14-28 days. It uses SerpApi’s Google Flights API and emails you the results with booking links. Perfect for snagging deals on a budget!

## Setting Up

Before running, you’ll need two things: a SerpApi key and an email app password.

### Getting Your SerpApi Key
1. Sign up at [SerpApi](https://serpapi.com/).
2. Go to your dashboard and grab your API key (it’s a long string of letters and numbers).
3. Replace `"SERP_API_KEY"` in the script with your key.

### Getting Your Email App Password
If you’re using Gmail (like most folks):
1. Go to your Google Account > **Security**.
2. Under "Signing in to Google," enable **2-Step Verification** if it’s not on.
3. Then, under "App passwords," click to generate one:
   - Select "Mail" as the app, "Other" as the device, and name it (e.g., "FlightFinder").
   - Copy the 16-character password it gives you.
4. Replace `"APP_PASSWORD"` in the script with this password.
5. Set `EMAIL_SENDER` to your Gmail (e.g., `yourname@gmail.com`) and `EMAIL_RECEIVER` to whoever’s getting the email (could be the same).

For other email providers, check their docs for SMTP app passwords or use a regular password if they don’t require 2FA.

## Instructions to Run

Here’s how to get this thing flying locally:

1. **Install Python**: Make sure you’ve got Python 3 installed (```python3 --version``` to check).
2. **Install `requests`**:

```
pip install requests 
```

#### Need Help? Ask Your Favorite LLM
Stuck on installing `requests`? I got help from Grok (built by xAI) to troubleshoot this. Just ask something like, "How do I install requests for Python?" Your fave LLM (Grok, ChatGPT, whatever) can walk you through it!

3. **Edit the Script**:
Open `flightsapi.py` and replace these variables:
- `SERPAPI_KEY = "your_serpapi_key_here"`
- `EMAIL_SENDER = "your_email@gmail.com"`
- `EMAIL_PASSWORD = "your_app_password"`
- `EMAIL_RECEIVER = "your_receiver_email@email.com"`
- Tweak `MAX_PRICE`, `MIN_DURATION`, or `MAX_DURATION` if you want different limits.

4. **Run It**:

```
python flightsapi.py
```
This runs it once, searches flights, and emails the results.

5. **Want Daily Emails at 5 AM EST?**:
- Comment out the current `def main()` (add `#` to each line).
- Uncomment the second `def main()` (remove the `#` from that block).
- Run it again with ```python flightsapi.py```, and it’ll wait ’til 5 AM EST daily to send emails.

## Hosting on AWS

To run this 24/7 without your laptop, host it on AWS. Here’s a simple way using EC2:

1. **Launch an EC2 Instance**:
- Sign into AWS, go to EC2, and click "Launch Instance."
- Pick "Ubuntu Server" (free tier works), t2.micro size.
- Download the `.pem` key file when prompted.

2. **Connect to Your Instance**:

```
    ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

3. **Set Up the Environment**:

```
   sudo apt update
   sudo apt install python3-pip
   pip3 install requests
```

4. **Upload the Script**:
From your local machine:

```
    scp -i your-key.pem flightsapi.py ubuntu@your-ec2-public-ip:~/flightsapi.py
```

5. **Run It**:
- SSH in again, then:

```
    python3 ~/flightsapi.py
```
- For daily runs, use the scheduled `main()` (uncommented as above) and run it in the background:

```
   nohup python3 ~/flightsapi.py &
```

6. **Keep It Running**:
- Use `screen` or `tmux` to keep the session alive after you log out:

```
   screen
   python3 ~/flightsapi.py

```
(Press `Ctrl+A, D` to detach, then exit SSH.)

**Note**: AWS free tier gives you 750 hours/month—plenty for one instance. Watch SerpApi usage, though; more airports = more API calls = more $$.

Lifes to short to be boring - hope this helps! Hmu with issues or PRs if you’ve got ideas to make this better or if youre a fine af shawty trying to slide 