## 1.2

### 1.2-2
```python
from math import e, log
from scipy.special import lambertw

ln2 = log(2, e)
x1 = (-8 / ln2) * lambertw(-ln2 / 8, k=0)  # 1.099
x2 = (-8 / ln2) * lambertw(-ln2 / 8, k=-1)  # 43.559
# n ranges from (1.099, 43.559), or [2, 43]
```

### 1.2-3
```python
from math import e, log
from scipy.special import lambertw

ln2 = log(2, e)
x1 = (-2 / ln2) * lambertw(-ln2 / 20, k=0)  # 0.104
x2 = (-2 / ln2) * lambertw(-ln2 / 20, k=-1)  # 14.325
# n ranges from (-inf, 0.104) and (14.325, +inf), or (-inf, 0] and [15, +inf)
```