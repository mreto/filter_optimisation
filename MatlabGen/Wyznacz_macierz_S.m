function [S,f,S11,S21] = Wyznacz_macierz_S(C,T,mesh,siatka_plot)
  
    
  Z0 = 120 * pi;
  c = 299792458;
  EPS0=1e-9/(36*pi);
  f=3e+9:1e+7:5e+9;
  
 
  
  %wyznaczenie wektora wêz³ów w których znajduj¹ siê przes³ony
  %wyznaczenie czestotliwosci i wektorow pobudzenia
  [V1w,V2w,kTE1,kTE2] = Wektor_pobudzenia_ALL(mesh);
  [W]=Porzadkuj_wektor_pobudzenia(V1w,V2w,mesh);
  %uporzadkowanie wektora pobudzenia
  if siatka_plot
      Wykres_siatki(mesh,1);
      hold on
      scatter(1000*mesh.p(find(W(:,1)~=0),1),1000*mesh.p(find(W(:,1)~=0),2),'filled','k')
      hold on
      scatter(1000*mesh.p(find(W(:,2)~=0),1),1000*mesh.p(find(W(:,2)~=0),2),'filled','g')
      title('Przed wycieciem PEC')
  end
  %wyciêcie wêz³ów z macierzy Ct, Tt, Bp na podstawie Ww
  [ Ct,Tt,Wp,meshx ] = Porzadkuj_macierz_ALL( C,T,W,mesh,siatka_plot);
  if siatka_plot
      Wykres_siatki(mesh,3);
      hold on
      scatter(1000*meshx.p(find(abs(Wp(:,1)~=0)),1),1000*meshx.p(find(abs(Wp(:,1)~=0)),2),'filled','k')
      hold on
      scatter(1000*meshx.p(find(abs(Wp(:,2)~=0)),1),1000*meshx.p(find(abs(Wp(:,2)~=0)),2),'filled','g')
      title('Po wycieciu PEC')
  end
    

  %(Ct - k^2 Tt)*x = B;
  %kcTE1, kcTE2 - cutoff frequency in waveguide ports
  
  %inicjalizacja
  S11=zeros(size(W,2),size(f,2));
  S21=zeros(size(W,2),size(f,2));
  NoS11F=zeros(size(W,2),size(f,2));
  NoS21F=zeros(size(W,2),size(f,2));
  
  
  tic
  for i=1:size(f,2)
      
      
      k0 = (2*pi*f(i))/c;
      % waveguide port impedance
      ZTE1 = Impedancja_Fali_TE( kTE1 ,f(i) );
      ZTE2 = Impedancja_Fali_TE( kTE2, f(i) ); 
      
      G = ( ( Ct - ((k0)^2) * Tt ));
      
      % normalization and solution
      Di = diag(sqrt([1/ZTE1 1/ZTE2]));
      WP = Wp * (Di); 
      x = G\WP;
                  
      % GAM
      Z2 = 1i * 2 * pi * f(i) * EPS0 * x' * WP ;
      Y2 = inv(Z2);
      ID = eye(size(Y2));
      % GSM
      S = 2 * inv( ID + Y2 ) - ID;
      S11(:,i)=20 * log10( abs(S(1,1)) );
      S21(:,i)=20 * log10( abs(S(2,1)) );
      NoS11F(:,i)=S(1,1);
      NoS21F(:,i)=S(2,1);
  end
  toc
  figure(5)
  plot(f/1e9,S11,'k-'); hold on;
  plot(f/1e9,S21,'r-');
  xlabel('f (GHz)')
  ylabel('|s_{11}|, |s_{21}| (dB)')
  
  %save symulacja_gigant.mat S11 S21 f;
  %save parametry_FEM.mat NoS11F NoS21F;
end