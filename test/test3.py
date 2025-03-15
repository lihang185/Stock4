import matplotlib.pyplot as plt


x= list(range(0, 36))
y=[6,3,9,2,6,16,8,10,4,14,18,6] * 3



plt.bar(x,y)
plt.rcParams['figure.dpi'] = 300  # 分辨率
plt.rcParams['figure.figsize'] = (15.0, 8.0)  # 尺寸
plt.show()
