function [ZTE] = Impedancja_Fali_TE(kcTE,f0)
  
  c = 299792458;
  mi0 = 4*pi*1e-7;
  k0 = (2*pi*f0)/c;
  GTE = 1/(sqrt( k0.^2 - kcTE.^2));
  evan = find(imag(GTE));
  GTE(evan) = 1i*abs(GTE(evan));
  ZTE = (2*pi*f0*mi0*GTE);
  
end