#!/usr/bin/env python3
"""Turn price options into checked totals for a proposal, so no math is done by hand.

Input JSON (sales/proposals/<slug>-prices.json):
{
  "currency": "USD",
  "options": [
    {"name": "Starter", "lines": [
        {"item": "Ledgerly seats", "unit_price": 29, "qty": 6, "per": "month"},
        {"item": "Setup and import", "unit_price": 0, "qty": 1, "per": "once"}],
     "discount_pct": 0, "term_months": 12}
  ],
  "cost_per_unit": {"Ledgerly seats": 4}          (optional, for margin)
}
"per" is "month", "week", "once" or "year". term_months turns recurring lines into a total
for the term (weeks use 52/12 weeks per month).

Prints a Markdown table with per-period and term totals, and margin when costs are given.
Usage: python3 price_options.py prices.json [--md out.md]
Standard library only.
"""
import argparse
import json
import sys

WEEKS_PER_MONTH = 52.0 / 12.0


def money(x, cur):
    sign = "-" if x < 0 else ""
    sym = {"USD": "$", "CAD": "CA$", "EUR": "EUR ", "GBP": "GBP "}.get(cur, cur + " ")
    return "%s%s%s" % (sign, sym, "{:,.2f}".format(abs(x)).replace(".00", ""))


def option_totals(opt, costs=None):
    costs = costs or {}
    term = float(opt.get("term_months", 12))
    monthly = once = cost_monthly = cost_once = 0.0
    for line in opt.get("lines", []):
        price = float(line["unit_price"]) * float(line.get("qty", 1))
        cost = float(costs.get(line["item"], 0)) * float(line.get("qty", 1))
        per = line.get("per", "month")
        if per == "month":
            monthly += price
            cost_monthly += cost
        elif per == "week":
            monthly += price * WEEKS_PER_MONTH
            cost_monthly += cost * WEEKS_PER_MONTH
        elif per == "year":
            monthly += price / 12.0
            cost_monthly += cost / 12.0
        elif per == "once":
            once += price
            cost_once += cost
        else:
            raise ValueError("per must be month, week, year or once: %r" % per)
    disc = float(opt.get("discount_pct", 0)) / 100.0
    if not 0 <= disc < 1:
        raise ValueError("discount_pct must be between 0 and 99")
    monthly_after = monthly * (1 - disc)
    term_total = monthly_after * term + once
    out = {
        "name": opt["name"], "monthly": monthly_after, "monthly_list": monthly,
        "once": once, "term_months": term, "term_total": term_total,
    }
    if costs:
        cost_total = cost_monthly * term + cost_once
        out["margin_pct"] = (100.0 * (term_total - cost_total) / term_total) if term_total else 0.0
    return out


def table(data):
    cur = data.get("currency", "USD")
    costs = data.get("cost_per_unit")
    rows = [option_totals(o, costs) for o in data["options"]]
    head = "| option | per month | one time | term | total for term |"
    sep = "| --- | --- | --- | --- | --- |"
    if costs:
        head += " margin |"
        sep += " --- |"
    lines = [head, sep]
    for r in rows:
        monthly = money(r["monthly"], cur)
        if r["monthly_list"] != r["monthly"]:
            monthly += " (list %s)" % money(r["monthly_list"], cur)
        term = r["term_months"]
        term_txt = "%g month%s" % (term, "" if term == 1 else "s")
        if r["monthly"] == 0 and r["once"] > 0:
            monthly, term_txt = "none", "one time"
        line = "| %s | %s | %s | %s | %s |" % (
            r["name"], monthly, money(r["once"], cur), term_txt, money(r["term_total"], cur))
        if costs:
            line += " %.0f%% |" % r["margin_pct"]
        lines.append(line)
    return "\n".join(lines) + "\n", rows


def main(argv=None):
    parser = argparse.ArgumentParser(description="Checked totals for proposal price options.")
    parser.add_argument("prices")
    parser.add_argument("--md")
    args = parser.parse_args(argv)
    try:
        with open(args.prices, encoding="utf-8") as fh:
            data = json.load(fh)
        if not 1 <= len(data.get("options", [])) <= 4:
            raise ValueError("give 1 to 4 options (2 or 3 is best)")
        md, rows = table(data)
    except (OSError, ValueError, KeyError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    sys.stdout.write(md)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as fh:
            fh.write(md)
    for r in rows:
        if "margin_pct" in r and r["margin_pct"] < 30:
            print("note: %s margin is %.0f%%, check this is on purpose" % (r["name"], r["margin_pct"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
