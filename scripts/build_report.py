from reportlab.pdfgen import canvas
import pandas as pd

df = pd.read_csv("..\\Results\\trade_ledger.csv")

c = canvas.Canvas("output/investor_report.pdf")

c.drawString(100, 800, "TRANSITION CAPITAL REPORT")

pnl = df["pnl"].sum()
win_rate = (df["pnl"] > 0).mean()

c.drawString(100, 760, f"Total PnL: {pnl:,.2f}")
c.drawString(100, 740, f"Win Rate: {win_rate*100:.2f}%")

c.save()

print("✅ PDF REPORT GENERATED")