import os
import json
import random
import google.generativeai as genai
from dotenv import load_dotenv

# FIX: API safety
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini if key exists
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")  # fast + free
else:
    model = None


def _ask_gemini(prompt):
    """Send prompt to Gemini and parse JSON response."""
    resp = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.7,
            "response_mime_type": "application/json",  # forces JSON output
        },
    )
    return json.loads(resp.text)


def _ask_gemini_text(prompt):
    """Send prompt to Gemini and return plain text response (for chat)."""
    resp = model.generate_content(
        prompt,
        generation_config={"temperature": 0.7},
    )
    return resp.text


# FIX: caching
_ai_cache = {}

def _make_cache_key(func_name, customer, **kwargs):
    """Stabilize dictionary/objects into string key for global cache lookup."""
    sorted_cust = str(sorted(customer.items()))
    stable_kwargs = {}
    for k, v in kwargs.items():
        if isinstance(v, dict):
            stable_kwargs[k] = str(sorted(v.items()))
        else:
            stable_kwargs[k] = str(v)
    sorted_kwargs = str(sorted(stable_kwargs.items()))
    return f"{func_name}_{sorted_cust}_{sorted_kwargs}"


# NEW: AI confidence score helper
def _calculate_confidence(customer):
    """Calculate AI confidence score (0-100) based on data availability and signal strength."""
    score = 50  # base confidence
    if customer.get("age"): score += 10
    if customer.get("city"): score += 10
    if customer.get("fav_category"): score += 10
    
    visits = customer.get("visits_per_month", 0)
    spent = customer.get("total_spent", 0)
    
    if visits > 15: score += 10
    elif visits > 5: score += 5
    
    if spent > 30000: score += 10
    elif spent > 10000: score += 5
    
    return min(99, score)


# FIX: AI cleanup
def clean_text(text):
    if not isinstance(text, str):
        return text
    # Clean standard HTML tags often outputted by LLMs
    cleaned = text.replace("</div>", "").replace("<div>", "")
    cleaned = cleaned.replace("</p>", "").replace("<p>", "")
    cleaned = cleaned.replace("</span>", "").replace("<span>", "")
    return cleaned.strip()


# ---------- 1. SEGMENTATION (existing) ----------
def segment_customer(customer):
    # FIX: caching
    cache_key = _make_cache_key("segment_customer", customer)
    if cache_key in _ai_cache:
        return _ai_cache[cache_key]

    if not model:
        res = _demo_segment(customer)
        _ai_cache[cache_key] = res
        return res

    prompt = f"""You are a marketing AI. Classify this customer into ONE segment:
[High-Value Loyalist, Cart Abandoner, Bargain Hunter, New Explorer].

Customer data:
{json.dumps(customer, indent=2)}

Return ONLY valid JSON: {{"segment": "...", "reason": "one short sentence", "confidence": <integer 0-100>}}"""

    # FIX: performance (error handling wrapper)
    try:
        res = _ask_gemini(prompt)
        if "confidence" not in res:
            res["confidence"] = _calculate_confidence(customer)
        _ai_cache[cache_key] = res
        return res
    except Exception as e:
        print("Gemini error (segment):", e)
        res = _demo_segment(customer)
        _ai_cache[cache_key] = res
        return res


# ---------- 2. PERSONALIZED CONTENT (existing) ----------
def generate_personalized_message(customer, segment):
    # FIX: caching
    cache_key = _make_cache_key("generate_personalized_message", customer, segment=segment)
    if cache_key in _ai_cache:
        return _ai_cache[cache_key]

    if not model:
        res = _demo_message(customer, segment)
        _ai_cache[cache_key] = res
        return res

    prompt = f"""You are an expert marketing copywriter. Create a HYPER-PERSONALIZED
promotional email for this customer.

Customer: {json.dumps(customer)}
Segment: {segment}

Return ONLY valid JSON with these exact keys:
{{
  "subject": "catchy personalized subject line with their name",
  "body": "3-4 sentence warm personalized email body",
  "recommended_product": "one specific product they'd love",
  "offer": "a custom discount/offer suited to their segment",
  "best_channel": "Email/SMS/WhatsApp/Push",
  "best_send_time": "based on their active_time",
  "reasoning": "1 sentence why this works for them",
  "confidence": <integer 0-100>
}}"""

    # FIX: performance (error handling wrapper)
    try:
        res = _ask_gemini(prompt)
        if "confidence" not in res:
            res["confidence"] = max(60, _calculate_confidence(customer) - random.randint(2, 8))
        _ai_cache[cache_key] = res
        return res
    except Exception as e:
        print("Gemini error (message):", e)
        res = _demo_message(customer, segment)
        _ai_cache[cache_key] = res
        return res


# ================================================================
# 3. CUSTOMER DNA PROFILE (existing)
# ================================================================
def generate_customer_dna(customer, segment=None):
    """Generate a Customer DNA profile with scores and predictions.
    Uses Gemini AI with intelligent rule-based fallback."""
    # FIX: caching
    seg_name = segment.get("segment") if isinstance(segment, dict) else segment
    cache_key = _make_cache_key("generate_customer_dna", customer, segment=seg_name)
    if cache_key in _ai_cache:
        return _ai_cache[cache_key]

    if not model:
        # FIX: consistency
        res = _demo_dna(customer, segment)
        _ai_cache[cache_key] = res
        return res

    # FIX: consistency
    seg_ctx = f"\nCustomer segment classification: {seg_name}" if seg_name else ""
    prompt = f"""You are a predictive analytics AI for an e-commerce platform.
Analyze this customer and generate a comprehensive "Customer DNA" profile.
{seg_ctx}

Customer data:
{json.dumps(customer, indent=2)}

Return ONLY valid JSON with these exact keys:
{{
  "intent_score": <integer 0-100, likelihood of purchase in next 7 days>,
  "engagement_score": <integer 0-100, how actively engaged they are>,
  "predicted_purchase": "<specific product category or item they'll likely buy next>",
  "churn_risk": "<Low/Medium/High — risk of becoming inactive>",
  "lifetime_value_estimate": <integer, estimated total lifetime value in INR>,
  "confidence": <integer 0-100>
}}"""

    # FIX: performance (error handling wrapper)
    try:
        res = _ask_gemini(prompt)
        if "confidence" not in res:
            res["confidence"] = _calculate_confidence(customer)
        # Verify predictability patterns
        spent = customer.get("total_spent", 0)
        visits = customer.get("visits_per_month", 0)
        abandoned = customer.get("cart_abandoned") == "Yes"
        if spent > 30000 and res.get("intent_score", 0) < 70:
            res["intent_score"] = random.randint(80, 95)
        if visits > 15 and res.get("engagement_score", 0) < 70:
            res["engagement_score"] = random.randint(80, 95)
        if abandoned:
            res["churn_risk"] = "High"
        _ai_cache[cache_key] = res
        return res
    except Exception as e:
        print("Gemini error (dna):", e)
        # FIX: consistency
        res = _demo_dna(customer, segment)
        _ai_cache[cache_key] = res
        return res


# ================================================================
# 4. AI PREDICTIONS (existing)
# ================================================================
def generate_predictions(customer, dna=None):
    """Predict future customer behavior — next action, timing, channel.
    Uses Gemini AI with intelligent rule-based fallback."""
    # FIX: caching
    dna_str = str(dna) if dna else ""
    cache_key = _make_cache_key("generate_predictions", customer, dna=dna_str)
    if cache_key in _ai_cache:
        return _ai_cache[cache_key]

    if not model:
        # FIX: consistency
        res = _demo_predictions(customer, dna)
        _ai_cache[cache_key] = res
        return res

    # FIX: consistency
    dna_ctx = f"\nCustomer DNA metrics: {json.dumps(dna)}" if dna else ""
    prompt = f"""You are a predictive customer behavior AI.
Based on this customer's data and DNA scores, predict their FUTURE behavior.
{dna_ctx}

Customer data:
{json.dumps(customer, indent=2)}

Return ONLY valid JSON with these exact keys:
{{
  "next_likely_action": "<specific next action e.g. 'Browse Sportswear', 'Complete abandoned cart', 'Redeem coupon'>",
  "purchase_probability": "<integer 0-100>",
  "best_time_to_engage": "<specific day and time, e.g. 'Tuesday Evening 6-8 PM'>",
  "best_channel": "<Email/SMS/WhatsApp/Push — with a short reason>",
  "mood": "<Excited/Curious/Hesitant/Loyal/Drifting — single word>",
  "confidence": <integer 0-100>
}}"""

    # FIX: performance (error handling wrapper)
    try:
        res = _ask_gemini(prompt)
        if "confidence" not in res:
            res["confidence"] = max(50, _calculate_confidence(customer) - random.randint(5, 12))
        # Ensure intent_score consistency
        if dna:
            intent_score = dna.get("intent_score", 50)
            res["purchase_probability"] = min(99, max(5, intent_score + random.randint(-5, 5)))
        _ai_cache[cache_key] = res
        return res
    except Exception as e:
        print("Gemini error (predictions):", e)
        # FIX: consistency
        res = _demo_predictions(customer, dna)
        _ai_cache[cache_key] = res
        return res


# ================================================================
# 5. AI EXPLANATION (existing)
# ================================================================
def generate_explanation(customer, segment, message):
    """Generate a 1-2 line AI explanation for why this recommendation was made.
    Uses Gemini AI with intelligent rule-based fallback."""
    # FIX: caching
    cache_key = _make_cache_key("generate_explanation", customer, segment=segment, subject=message.get("subject"))
    if cache_key in _ai_cache:
        return _ai_cache[cache_key]

    if not model:
        res = clean_text(_demo_explanation(customer, segment))
        _ai_cache[cache_key] = res
        return res

    prompt = f"""You are an explainable AI system. A marketing AI just generated a
personalized message for this customer.

Customer: {json.dumps(customer)}
Segment: {segment}
Generated message subject: {message.get('subject', '')}
Recommended product: {message.get('recommended_product', '')}

In exactly 1-2 sentences, explain WHY this recommendation was made.
Focus on the data signals that drove the decision.

Return ONLY valid JSON: {{"explanation": "1-2 sentence explanation"}}"""

    # FIX: performance (error handling wrapper)
    try:
        result = _ask_gemini(prompt)
        res = clean_text(result.get("explanation", "Recommendation based on customer behavior patterns."))
        _ai_cache[cache_key] = res
        return res
    except Exception as e:
        print("Gemini error (explanation):", e)
        res = clean_text(_demo_explanation(customer, segment))
        _ai_cache[cache_key] = res
        return res


# ================================================================
# NEW — 6. BUSINESS STRATEGY RECOMMENDER
# ================================================================
def generate_business_strategy(customer, dna=None, predictions=None):
    """Generate an AI-recommended business action for this customer.
    Uses Gemini AI with intelligent rule-based fallback."""
    # FIX: caching
    dna_str = str(dna) if dna else ""
    pred_str = str(predictions) if predictions else ""
    cache_key = _make_cache_key("generate_business_strategy", customer, dna=dna_str, predictions=pred_str)
    if cache_key in _ai_cache:
        return _ai_cache[cache_key]

    if not model:
        # FIX: consistency
        res = _demo_strategy(customer, dna, predictions)
        _ai_cache[cache_key] = res
        return res

    # FIX: consistency
    dna_ctx = f"\nCustomer DNA details: {json.dumps(dna)}" if dna else ""
    pred_ctx = f"\nCustomer behavior predictions: {json.dumps(predictions)}" if predictions else ""
    prompt = f"""You are a senior e-commerce strategist AI.
Analyze this customer's behavioral DNA and predictions to recommend the SINGLE BEST business action to maximize revenue.
{dna_ctx}
{pred_ctx}

Customer data:
{json.dumps(customer, indent=2)}

Return ONLY valid JSON with these exact keys:
{{
  "best_action": "<specific, actionable business recommendation>",
  "expected_outcome": "<quantified expected result, e.g. '35% higher conversion'>",
  "reason": "<1-2 sentence data-driven reasoning>",
  "priority": "<High/Medium/Low>",
  "action_type": "<Retention/Upsell/Win-back/Engagement/Conversion>",
  "confidence": <integer 0-100>
}}"""

    # FIX: performance (error handling wrapper)
    try:
        res = _ask_gemini(prompt)
        if "confidence" not in res:
            res["confidence"] = max(55, _calculate_confidence(customer) - random.randint(3, 7))
        # Strategy override consistency
        if dna and dna.get("churn_risk") == "High":
            res["priority"] = "High"
            if customer.get("cart_abandoned") == "Yes":
                res["action_type"] = "Conversion"
            else:
                res["action_type"] = "Retention"
        _ai_cache[cache_key] = res
        return res
    except Exception as e:
        print("Gemini error (strategy):", e)
        # FIX: consistency
        res = _demo_strategy(customer, dna, predictions)
        _ai_cache[cache_key] = res
        return res


# ================================================================
# NEW — 7. DIGITAL TWIN TIMELINE DATA
# ================================================================
# FIX: caching
_timeline_cache = {}

def generate_timeline_data(customer):
    """Generate simulated 30-day past + 7-day future timeline data.
    Returns lists of dates, engagement scores, and spending amounts."""
    # FIX: caching
    cache_key = customer.get("name", "unknown")
    if cache_key in _timeline_cache:
        return _timeline_cache[cache_key]

    import datetime
    import datetime as dt

    today = dt.date.today()
    visits = customer.get("visits_per_month", 10)
    spent = customer.get("total_spent", 10000)
    abandoned = customer.get("cart_abandoned", "No") == "Yes"
    aov = customer.get("avg_order_value", 3000)

    # Base daily engagement (derived from monthly visits)
    base_eng = min(95, max(15, visits * 3.5))
    # Base daily spend rate
    daily_spend_base = spent / 30

    dates = []
    engagement = []
    spending = []

    random.seed(hash(customer.get("name", "x")) % 10000)  # deterministic per customer

    # --- Past 30 days ---
    for i in range(-30, 0):
        d = today + datetime.timedelta(days=i)
        dates.append(d.isoformat())

        # Engagement: trend upward if high visits, downward if low
        day_noise = random.uniform(-12, 12)
        trend = (i + 30) / 30  # 0 -> 1 over 30 days
        if visits > 15:
            eng_val = base_eng * (0.7 + 0.3 * trend) + day_noise
        elif visits < 5:
            eng_val = base_eng * (1.1 - 0.3 * trend) + day_noise
        else:
            eng_val = base_eng + day_noise
        engagement.append(max(5, min(100, round(eng_val, 1))))

        # Spending: occasional spikes
        spike = random.choice([1, 1, 1, 1, 1.8, 2.5]) if random.random() > 0.6 else 1
        spend_val = daily_spend_base * spike * random.uniform(0.4, 1.6)
        spending.append(max(0, round(spend_val)))

    # --- Today ---
    dates.append(today.isoformat())
    engagement.append(max(5, min(100, round(base_eng + random.uniform(-5, 5), 1))))
    spending.append(round(daily_spend_base * random.uniform(0.8, 1.2)))

    # --- Future 7 days (PREDICTIONS) ---
    for i in range(1, 8):
        d = today + datetime.timedelta(days=i)
        dates.append(d.isoformat())

        # Future engagement: rises with intervention scenario
        future_trend = i / 7
        if abandoned:
            # Cart abandoners: engagement dips then recovers if re-engaged
            eng_val = base_eng * (0.8 + 0.25 * future_trend) + random.uniform(-5, 8)
        elif visits > 15:
            eng_val = base_eng * (1.0 + 0.15 * future_trend) + random.uniform(-3, 6)
        else:
            eng_val = base_eng * (0.9 + 0.1 * future_trend) + random.uniform(-8, 5)
        engagement.append(max(5, min(100, round(eng_val, 1))))

        # Future spending: gradual increase predicted
        spend_val = daily_spend_base * (1 + 0.1 * future_trend) * random.uniform(0.7, 1.5)
        spending.append(max(0, round(spend_val)))

    result = {
        "dates": dates,
        "engagement": engagement,
        "spending": spending,
        "today_index": 30,  # index of today in the arrays
    }
    _timeline_cache[cache_key] = result
    return result


# ================================================================
# NEW: Timeline insight
# ================================================================
def generate_timeline_interpretation(timeline, customer):
    """Generate AI interpretation of the customer's behavior timeline.
    Highlights spike days, drop patterns, and engagement trends."""
    # FIX: performance (error handling wrapper)
    try:
        dates = timeline["dates"]
        engagement = timeline["engagement"]
        spending = timeline["spending"]
        today_idx = timeline["today_index"]
        
        # Split past vs future
        past_eng = engagement[:today_idx]
        future_eng = engagement[today_idx:]
        past_spend = spending[:today_idx]
        
        # Analyze spikes and drops in engagement
        max_eng = max(past_eng)
        min_eng = min(past_eng)
        avg_eng = sum(past_eng) / len(past_eng)
        
        # Spike days
        spike_indices = [i for i, x in enumerate(past_eng) if x > avg_eng + 10]
        spike_dates = [dates[i] for i in spike_indices]
        
        # Drop patterns
        drop_indices = [i for i, x in enumerate(past_eng) if x < avg_eng - 10]
        drop_dates = [dates[i] for i in drop_indices]
        
        # Trends
        future_trend = "stable"
        if future_eng[-1] > future_eng[0] + 5:
            future_trend = "rising"
        elif future_eng[-1] < future_eng[0] - 5:
            future_trend = "declining"
            
        past_trend = "stable"
        if past_eng[-1] > past_eng[0] + 5:
            past_trend = "rising"
        elif past_eng[-1] < past_eng[0] - 5:
            past_trend = "declining"
            
        # Build interpretation
        name = customer.get("name", "Customer")
        cat = customer.get("fav_category", "products")
        
        narrative = ""
        if past_trend == "rising":
            narrative += f"📈 **Engagement rising:** Over the past 30 days, {name}'s interest has steadily increased. "
        elif past_trend == "declining":
            narrative += f"🚨 **Spending drop / Churn risk:** We notice a downward trend in {name}'s engagement, signaling a potential churn risk. "
        else:
            narrative += f"🔄 **Engagement stable:** {name} maintains a steady, consistent level of activity. "
            
        if future_trend == "rising":
            narrative += f"🎯 **High conversion opportunity:** AI predicts engagement will peak in the next 7 days. This is the optimal time to send a personalized offer for {cat}."
        elif future_trend == "declining":
            narrative += f"⚠️ **Retention warning:** AI predicts a drop in engagement next week. A proactive retention campaign is recommended."
        else:
            narrative += f"💬 **Standard nurturing recommended:** Steady activity predicted. Continue regular engagement."
            
        # Highlights of spikes and drops
        highlights = []
        if spike_dates:
            # Get the highest spending day
            max_spend = max(past_spend)
            if max_spend > 0:
                max_spend_idx = past_spend.index(max_spend)
                max_spend_date = dates[max_spend_idx]
                highlights.append(f"⭐ **Purchase Spike:** A peak spend of ₹{max_spend:,} was recorded on {max_spend_date}.")
            else:
                highlights.append(f"⚡ **Engagement Spike:** High engagement was noted around {spike_dates[-1]}.")
                
        if drop_dates:
            highlights.append(f"⚠️ **Inactivity Period:** Low engagement patterns were identified around {drop_dates[-1]}, indicating temporary drop-offs.")
            
        if not highlights:
            highlights.append("✨ **Consistent Behavior:** No extreme spikes or drops in the past 30 days. Steady loyalty.")
            
        # Let's mock a generative prompt if Gemini is enabled, else return narrative
        if model:
            prompt = f"""You are a customer behavior analyst. Summarize this customer's 30-day history and 7-day prediction.
Customer name: {name}
Product category: {cat}
Past engagement: {past_eng[-5:]} (recent 5 days)
Future engagement: {future_eng} (next 7 days)
Past spending: {past_spend[-5:]} (recent 5 days)

Write a 2-3 sentence AI timeline interpretation. Mention specific patterns (e.g. rising/dropping engagement, spike days).
Use bold highlights like 'Engagement rising → high conversion opportunity' or 'Spending drop → churn risk'.
Return ONLY valid JSON: {{"interpretation": "...", "highlights": ["...", "..."]}}"""
            try:
                res = _ask_gemini(prompt)
                return {
                    "interpretation": res.get("interpretation", narrative),
                    "highlights": res.get("highlights", highlights)
                }
            except Exception:
                pass
                
        return {
            "interpretation": narrative,
            "highlights": highlights
        }
    except Exception as e:
        print("Error in generate_timeline_interpretation:", e)
        return {
            "interpretation": "Analysis unavailable. Steady behavior predicted.",
            "highlights": ["Consistent engagement baseline."]
        }


# ================================================================
# NEW — 8. WHAT-IF SIMULATION ENGINE
# ================================================================
def simulate_whatif(customer, scenario):
    """Simulate a what-if scenario and return before/after metrics.
    scenario: '20% Discount' | 'Evening Campaign' | 'Retention Offer'"""
    # FIX: performance (error handling wrapper)
    try:
        # FIX: consistency
        seg = segment_customer(customer)
        dna = generate_customer_dna(customer, segment=seg)
        preds = generate_predictions(customer, dna=dna)

        base_prob = int(preds.get("purchase_probability", 40))
        base_conv = round(base_prob * 0.045, 1)  # rough conversion rate
        base_revenue = customer.get("total_spent", 10000)
        monthly_revenue = round(base_revenue / 12)

        if scenario == "20% Discount":
            prob_lift = random.randint(18, 30)
            conv_lift = round(prob_lift * 0.05, 1)
            rev_change = round(monthly_revenue * (prob_lift / 100) * 0.8)  # 80% of lift (discount cost)
            insight = "Price-sensitive customers show 2-3x higher response to discount triggers."
        elif scenario == "Evening Campaign":
            active = customer.get("active_time", "Evening")
            if active in ("Evening", "Night"):
                prob_lift = random.randint(12, 22)
            else:
                prob_lift = random.randint(3, 10)
            conv_lift = round(prob_lift * 0.04, 1)
            rev_change = round(monthly_revenue * (prob_lift / 100))
            insight = f"Customer is most active during {active}. " + (
                "Evening alignment maximizes open rates." if active in ("Evening", "Night")
                else "Timing mismatch may reduce impact — consider their preferred window."
            )
        elif scenario == "Retention Offer":
            churn = dna.get("churn_risk", "Medium")
            if churn == "High":
                prob_lift = random.randint(22, 38)
            elif churn == "Medium":
                prob_lift = random.randint(12, 22)
            else:
                prob_lift = random.randint(5, 12)
            conv_lift = round(prob_lift * 0.04, 1)
            rev_change = round(monthly_revenue * (prob_lift / 100) * 1.2)  # retention has high ROI
            insight = f"Churn risk is {churn}. " + (
                "Retention offers for high-risk users yield 3-5x ROI." if churn == "High"
                else "Proactive retention strengthens loyalty."
            )
        else:
            prob_lift = 10
            conv_lift = 0.5
            rev_change = round(monthly_revenue * 0.1)
            insight = "Generic scenario applied."

        return {
            "before": {
                "purchase_probability": base_prob,
                "conversion_rate": base_conv,
                "monthly_revenue": monthly_revenue,
            },
            "after": {
                "purchase_probability": min(99, base_prob + prob_lift),
                "conversion_rate": round(base_conv + conv_lift, 1),
                "monthly_revenue": monthly_revenue + rev_change,
            },
            "lift": {
                "probability_lift": f"+{prob_lift}%",
                "conversion_lift": f"+{conv_lift}%",
                "revenue_impact": f"+₹{rev_change:,}",
            },
            "insight": insight,
            "confidence": max(60, _calculate_confidence(customer) - random.randint(3, 8))
        }
    except Exception as e:
        print("Error in simulate_whatif:", e)
        return {
            "before": {"purchase_probability": 40, "conversion_rate": 1.8, "monthly_revenue": 1000},
            "after": {"purchase_probability": 50, "conversion_rate": 2.2, "monthly_revenue": 1100},
            "lift": {"probability_lift": "+10%", "conversion_lift": "+0.4%", "revenue_impact": "+₹100"},
            "insight": "Error simulating scenario. Showing fallback projection.",
            "confidence": 50
        }


# ================================================================
# NEW — 9. AI CHAT ASSISTANT (Ask PersonaX AI)
# ================================================================
# NEW: Chat improvement
def ask_personax(question, customer=None, context=""):
    """Answer marketing questions using Gemini AI or fallback.
    Optionally takes a customer context and global context for personalized, business-focused answers."""
    if not model:
        return clean_text(_demo_chat(question, customer, context))

    customer_ctx = ""
    if customer:
        customer_ctx = f"\nCurrent customer context:\n{json.dumps(customer, indent=2)}"

    prompt = f"""You are PersonaX AI — an expert marketing strategist and customer analytics assistant.
Provide an actionable, specific, and business-focused answer to the user's question (2-4 sentences max).
Incorporate customer context and portfolio summary details if available to give direct recommendations.

{customer_ctx}
{f"Additional context (Portfolio Metrics): {context}" if context else ""}

User question: {question}

Respond in clean, professional plain text (not JSON). Be helpful, strategic, and highly specific."""

    # FIX: performance (error handling wrapper)
    try:
        return clean_text(_ask_gemini_text(prompt))
    except Exception as e:
        print("Gemini error (chat):", e)
        return clean_text(_demo_chat(question, customer, context))


# ================================================================
# NEW — 10. INSIGHT SUMMARY (Mini Story Mode)
# ================================================================
def generate_insight_summary(customer, dna=None, predictions=None):
    """Generate a 2-3 sentence AI analyst narrative about this customer.
    Combines DNA + prediction data into an actionable story.
    Uses Gemini AI with intelligent rule-based fallback."""

    # Build context from pre-computed data if available
    ctx = ""
    if dna:
        ctx += f"\nDNA: Intent={dna.get('intent_score')}, Engagement={dna.get('engagement_score')}, Churn={dna.get('churn_risk')}, LTV=₹{dna.get('lifetime_value_estimate', 0):,}"
    if predictions:
        ctx += f"\nPredictions: Next action={predictions.get('next_likely_action')}, Purchase prob={predictions.get('purchase_probability')}%, Best channel={predictions.get('best_channel')}, Mood={predictions.get('mood')}"

    # FIX: caching
    cache_key = _make_cache_key("generate_insight_summary", customer, dna=str(dna), predictions=str(predictions))
    if cache_key in _ai_cache:
        return _ai_cache[cache_key]

    if not model:
        res = _demo_insight_summary(customer, dna, predictions)
        res["summary"] = clean_text(res.get("summary", ""))
        _ai_cache[cache_key] = res
        return res

    prompt = f"""You are a senior AI marketing analyst presenting a brief insight to a business owner.
Given this customer's data and AI analysis, write a 2-3 sentence executive summary.
Be specific (use names, numbers, product categories). Make it feel like a live AI analyst briefing.
End with one clear action recommendation.

Customer: {json.dumps(customer)}
{ctx}

Return ONLY valid JSON with these exact keys:
{{
  "summary": "2-3 sentence insight summary",
  "confidence": <integer 0-100>
}}"""

    # FIX: performance (error handling wrapper)
    try:
        res = _ask_gemini(prompt)
        if "confidence" not in res:
            res["confidence"] = _calculate_confidence(customer)
        res["summary"] = clean_text(res.get("summary", ""))
        _ai_cache[cache_key] = res
        return res
    except Exception as e:
        print("Gemini error (insight):", e)
        res = _demo_insight_summary(customer, dna, predictions)
        res["summary"] = clean_text(res.get("summary", ""))
        _ai_cache[cache_key] = res
        return res


# ================================================================
# PERFORMANCE: Simple response cache to limit redundant API calls
# ================================================================
_response_cache = {}

def _cached_call(func, cache_key, *args, **kwargs):
    """Simple cache wrapper — avoids redundant Gemini calls for same input."""
    if cache_key in _response_cache:
        return _response_cache[cache_key]
    result = func(*args, **kwargs)
    _response_cache[cache_key] = result
    # Keep cache bounded (max 200 entries)
    if len(_response_cache) > 200:
        oldest = next(iter(_response_cache))
        del _response_cache[oldest]
    return result


# ================================================================
# DEMO FALLBACKS (work without ANY API key)
# ================================================================

def _demo_segment(c):
    res = {}
    if c.get("cart_abandoned") == "Yes":
        res = {"segment": "Cart Abandoner", "reason": "Left items in cart without checkout."}
    elif c.get("total_spent", 0) > 30000:
        res = {"segment": "High-Value Loyalist", "reason": "High total spend & frequent visits."}
    elif c.get("avg_order_value", 9999) < 1000:
        res = {"segment": "Bargain Hunter", "reason": "Low order value, deal-seeking behavior."}
    else:
        res = {"segment": "New Explorer", "reason": "Recently active, exploring categories."}
    res["confidence"] = _calculate_confidence(c)
    return res


def _demo_message(c, seg):
    res = {
        "subject": f"{c['name']}, your {c['fav_category']} pick is waiting! 🎁",
        "body": f"Hi {c['name']}, we noticed you love {c['fav_category']}. "
                f"Based on your recent interest in {c['last_purchase']}, "
                f"we picked something special just for you. Don't miss out!",
        "recommended_product": f"Premium {c['fav_category']} Bundle",
        "offer": "15% OFF" if seg == "Bargain Hunter" else "Early access + free shipping",
        "best_channel": "WhatsApp" if c.get("age", 30) < 30 else "Email",
        "best_send_time": c.get("active_time", "Evening"),
        "reasoning": f"Tailored to a {seg} who shops in {c['fav_category']}.",
    }
    res["confidence"] = max(60, _calculate_confidence(c) - random.randint(2, 8))
    return res


# Fallback: Customer DNA
# FIX: consistency
def _demo_dna(c, segment=None):
    """Intelligent rule-based DNA scoring when Gemini is unavailable."""
    spent = c.get("total_spent", 0)
    visits = c.get("visits_per_month", 0)
    aov = c.get("avg_order_value", 0)
    abandoned = c.get("cart_abandoned", "No") == "Yes"

    # FIX: consistency rule-based logic (predictable baseline)
    # High visits -> high engagement
    if visits > 15:
        engagement = random.randint(80, 98)
    elif visits > 5:
        engagement = random.randint(50, 79)
    else:
        engagement = random.randint(15, 49)

    # High spend -> high intent
    if spent > 30000:
        intent = random.randint(80, 98)
    elif spent > 10000:
        intent = random.randint(50, 79)
    else:
        intent = random.randint(15, 49)

    # Cart abandoned -> high churn
    if abandoned:
        churn = "High"
        intent = max(intent, random.randint(70, 85))  # abandoned cart signals strong baseline interest
    else:
        if visits > 10 and spent > 20000:
            churn = "Low"
        elif visits <= 4:
            churn = "High"
        else:
            churn = "Medium"

    # Segment alignment overrides
    if segment:
        seg_name = segment if isinstance(segment, str) else segment.get("segment")
        if seg_name == "High-Value Loyalist":
            engagement = max(engagement, 80)
            intent = max(intent, 80)
            churn = "Low"
        elif seg_name == "Cart Abandoner":
            intent = max(intent, 70)
            churn = "High"
        elif seg_name == "Bargain Hunter":
            churn = "Medium"

    predicted = f"Premium {c.get('fav_category', 'Product')} item"
    ltv = int(spent * (visits / 5) * 1.3)

    return {
        "intent_score": intent,
        "engagement_score": engagement,
        "predicted_purchase": predicted,
        "churn_risk": churn,
        "lifetime_value_estimate": max(ltv, spent),
        "confidence": _calculate_confidence(c),
    }


# Fallback: Predictions
# FIX: consistency
def _demo_predictions(c, dna=None):
    """Intelligent rule-based predictions when Gemini is unavailable."""
    abandoned = c.get("cart_abandoned", "No") == "Yes"
    visits = c.get("visits_per_month", 0)
    age = c.get("age", 30)
    active = c.get("active_time", "Evening")
    cat = c.get("fav_category", "Products")

    # FIX: consistency with DNA
    intent_score = 50
    churn_risk = "Medium"
    if dna:
        intent_score = dna.get("intent_score", 50)
        churn_risk = dna.get("churn_risk", "Medium")
    else:
        intent_score = 85 if c.get("total_spent", 0) > 30000 else 45
        churn_risk = "High" if abandoned else ("Low" if visits > 10 else "Medium")

    # Purchase probability aligns with DNA intent_score
    prob = min(99, max(5, intent_score + random.randint(-5, 5)))

    # Mood aligns with churn_risk and visits
    if churn_risk == "High" and abandoned:
        mood = "Hesitant"
        action = f"Complete abandoned cart purchase in {cat}"
    elif churn_risk == "High":
        mood = "Drifting"
        action = f"Explore {cat} deals and discounts"
    elif visits > 15:
        mood = "Loyal"
        action = f"Browse new arrivals in {cat}"
    else:
        mood = "Curious"
        action = f"Compare {cat} products and read reviews"

    time_map = {
        "Morning": "Weekday Morning 9-11 AM",
        "Afternoon": "Weekend Afternoon 2-4 PM",
        "Evening": "Tuesday Evening 6-8 PM",
        "Night": "Friday Night 9-11 PM",
    }

    if age < 25:
        channel = "Instagram DM — Gen-Z preferred channel"
    elif age < 35:
        channel = "WhatsApp — high open rate for millennials"
    elif age < 50:
        channel = "Email — professional and detailed"
    else:
        channel = "SMS — simple and direct"

    return {
        "next_likely_action": action,
        "purchase_probability": prob,
        "best_time_to_engage": time_map.get(active, "Evening 6-8 PM"),
        "best_channel": channel,
        "mood": mood,
        "confidence": max(50, _calculate_confidence(c) - random.randint(5, 12)),
    }


# Fallback: Explanation
def _demo_explanation(c, seg):
    """Rule-based explanation when Gemini is unavailable."""
    name = c.get("name", "Customer")
    cat = c.get("fav_category", "products")
    spent = c.get("total_spent", 0)
    visits = c.get("visits_per_month", 0)

    if seg == "Cart Abandoner":
        return (f"{name} abandoned their cart, signaling strong purchase intent. "
                f"A targeted nudge with urgency can recover this sale.")
    elif seg == "High-Value Loyalist":
        return (f"{name} has spent ₹{spent:,} across {visits} monthly visits, "
                f"making them ideal for exclusive loyalty rewards in {cat}.")
    elif seg == "Bargain Hunter":
        return (f"{name}'s low average order value suggests price sensitivity. "
                f"Discount-led offers in {cat} will drive conversion.")
    else:
        return (f"{name} is actively exploring {cat} with {visits} visits/month. "
                f"Discovery-focused content will deepen engagement.")


# NEW — Fallback: Business Strategy
# FIX: consistency
def _demo_strategy(c, dna=None, predictions=None):
    """Rule-based strategy when Gemini is unavailable."""
    abandoned = c.get("cart_abandoned", "No") == "Yes"
    spent = c.get("total_spent", 0)
    visits = c.get("visits_per_month", 0)
    cat = c.get("fav_category", "Products")
    name = c.get("name", "Customer")

    # FIX: consistency checks
    churn_risk = "Medium"
    intent_score = 50
    prob = 50
    if dna:
        churn_risk = dna.get("churn_risk", "Medium")
        intent_score = dna.get("intent_score", 50)
    if predictions:
        prob = predictions.get("purchase_probability", 50)

    if churn_risk == "High" and abandoned:
        best_action = f"Send {name} an urgent cart recovery email with free shipping on {cat}"
        expected_outcome = "40-55% cart recovery rate, est. ₹3,000+ recovered revenue"
        reason = (f"High churn risk customer ({name}) with abandoned cart signals strong purchase intent. "
                  f"Cart recovery emails have 3x higher conversion than regular campaigns.")
        priority = "High"
        action_type = "Conversion"
    elif churn_risk == "High":
        best_action = f"Launch a personalized win-back email sequence for {name} with {cat} recommendations"
        expected_outcome = "18-25% re-engagement rate within 14 days"
        reason = (f"Low visit frequency ({visits}/mo) and high churn risk signals disengagement. "
                  f"Personalized win-back sequences prevent churn before it becomes permanent.")
        priority = "High"
        action_type = "Retention"
    elif intent_score > 75 and spent > 30000:
        best_action = f"Enroll {name} in VIP loyalty program with early access to {cat} launches"
        expected_outcome = "20% increase in order frequency, 30% higher AOV"
        reason = f"{name} is a high-value customer (₹{spent:,} spend, {visits} visits/mo) and intent score {intent_score}/100. VIP perks maximize LTV."
        priority = "Medium"
        action_type = "Upsell"
    else:
        best_action = f"Send {name} a curated {cat} collection based on browsing history"
        expected_outcome = "15-22% conversion rate on recommendations"
        reason = f"{name} shows steady engagement ({visits} visits/mo). Curated recommendations drive incremental conversion."
        priority = "Medium"
        action_type = "Engagement"

    res = {
        "best_action": best_action,
        "expected_outcome": expected_outcome,
        "reason": reason,
        "priority": priority,
        "action_type": action_type,
    }
    res["confidence"] = max(55, _calculate_confidence(c) - random.randint(3, 7))
    return res


# NEW — Fallback: Chat
# NEW: Chat improvement
def _demo_chat(question, customer=None, context=""):
    """Simple keyword-based fallback for chat when Gemini is unavailable."""
    q = question.lower()
    cust_info = f" for customer {customer['name']}" if customer else ""
    ctx_info = f" (Context details: {context})" if context else ""
    
    if any(w in q for w in ["churn", "retain", "losing"]):
        return (f"Based on our predictive analysis, we currently have some at-risk customers{ctx_info}. "
                f"To reduce churn, focus on customers with low monthly visits. "
                f"For {customer['name'] if customer else 'at-risk users'}, send an immediate "
                f"personalized WhatsApp message with a retention coupon. Historically, "
                f"targeting high-churn users recovers 30% of at-risk revenue.")
    elif any(w in q for w in ["revenue", "increase", "grow", "sales"]):
        return (f"To grow revenue, focus on the top performing city and segment{ctx_info}. "
                f"For {customer['name'] if customer else 'loyalists'}, offer VIP early access to products. "
                f"Evening campaigns are showing 22% higher average order value (AOV) on average.")
    elif any(w in q for w in ["segment", "audience", "target"]):
        return (f"Our current segment structure highlights High-Value Loyalists as our most lucrative cluster{ctx_info}. "
                f"For {customer['name'] if customer else 'general outreach'}, tailor messaging using the "
                f"Personalize tab where AI classifies users into one of four behavioral segments.")
    elif any(w in q for w in ["campaign", "email", "message"]):
        return (f"For campaigns{cust_info}, trigger push notifications or emails aligned with their active time. "
                f"Deploying personalized content yields 4x higher CTR compared to static campaigns. "
                f"Check the Personalize page to get the exact AI-generated draft.")
    else:
        return (f"I'm PersonaX AI, your business growth assistant. {ctx_info} "
                f"I recommend analyzing the Customer DNA and What-If Lab to see "
                f"potential lift. Let me know if you want target recommendations or churn reduction tips!")


# NEW — Fallback: Insight Summary (Mini Story Mode)
def _demo_insight_summary(c, dna=None, predictions=None):
    """Rule-based insight summary when Gemini is unavailable."""
    name = c.get("name", "Customer")
    cat = c.get("fav_category", "products")
    spent = c.get("total_spent", 0)
    visits = c.get("visits_per_month", 0)
    abandoned = c.get("cart_abandoned", "No") == "Yes"
    active = c.get("active_time", "Evening")

    # Use DNA data if available, otherwise compute inline
    if dna:
        intent = dna.get("intent_score", 50)
        engagement = dna.get("engagement_score", 50)
        churn = dna.get("churn_risk", "Medium")
    else:
        intent = min(100, int(visits * 3.5 + (c.get("avg_order_value", 0) / 100)))
        engagement = min(100, int(visits * 4 + (spent / 1000)))
        churn = "High" if visits <= 3 and spent < 10000 else ("Low" if visits > 8 and spent > 20000 else "Medium")

    prob = predictions.get("purchase_probability", 50) if predictions else (70 if visits > 10 else 35)
    channel = predictions.get("best_channel", "Email") if predictions else "Email"

    summary = ""
    # Build narrative based on signals
    if abandoned and intent > 60:
        summary = (f"{name} shows strong purchase intent (score: {intent}/100) despite abandoning their cart. "
                f"Their engagement with {cat} remains active at {engagement}/100. "
                f"A targeted {channel.split('—')[0].strip()} recovery message during {active.lower()} hours "
                f"could convert this into a ₹{c.get('avg_order_value', 3000):,}+ sale.")
    elif churn == "High":
        summary = (f"⚠️ {name} is at high risk of churning — only {visits} visits/month with "
                f"₹{spent:,} total spend. Engagement has dropped to {engagement}/100. "
                f"Recommend an immediate personalized retention offer via {channel.split('—')[0].strip()} "
                f"to prevent losing this customer.")
    elif intent > 75 and engagement > 70:
        summary = (f"{name} is a prime conversion opportunity — intent is {intent}/100 with "
                f"{engagement}/100 engagement. They have a {prob}% purchase probability for {cat}. "
                f"Deploy a {channel.split('—')[0].strip()} campaign during {active.lower()} hours "
                f"to capture this high-probability sale.")
    elif spent > 30000:
        summary = (f"{name} is a high-value customer (₹{spent:,} lifetime spend) who loves {cat}. "
                f"With {visits} visits/month and {engagement}/100 engagement, they're primed for upselling. "
                f"Consider exclusive VIP offers or early access to new {cat} collections "
                f"to maximize their lifetime value.")
    else:
        summary = (f"{name} shows moderate engagement ({engagement}/100) with a focus on {cat}. "
                f"Their purchase probability sits at {prob}%, with best engagement window during {active.lower()} hours. "
                f"A curated {cat} recommendation via {channel.split('—')[0].strip()} "
                f"can nudge them toward their next purchase.")
                
    return {
        "summary": summary,
        "confidence": _calculate_confidence(c)
    }