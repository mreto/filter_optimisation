% get data
x = csvread('x.csv');
y = csvread('y.csv');
z = csvread('z.csv');
d1 = csvread('D13.csv');
d2 = csvread('D2.csv');
S = csvread('S.csv');

surf(d1, d2, S, 'faceAlpha', 0.6)
hold on
p = plot3(x, y, z, 'r', 'LineWidth', 5)
title('F(3.4, 2.7) - F(D13, D2)')
xlabel("D13")
ylabel("D2")

% set plot in front of surf
h = get(gca,'Children');
set(gca,'Children',[h(2) h(1)])

hold off
