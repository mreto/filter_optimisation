d1 = csvread('D13.csv');
d2 = csvread('D2.csv');
S = csvread('S.csv');
surf(d1, d2, S)
title('F(3.3, 4.6) - F(D13, D2)')
xlabel("D13")
ylabel("D2")
