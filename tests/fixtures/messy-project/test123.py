# 할인율 실험용 스크립트 — 나중에 지울 것
rates = [0.03, 0.05, 0.07, 0.1]

for rate in rates:
    sample = 48000
    discounted = sample * (1 - rate)
    print(rate, int(discounted))

if True:
    print("배송비 포함:", int(48000 * 0.95) + 3000)

print("done")
