function Load_Points()

  ## IMPORTANT NOTE I have commented all the data... lines without it the matlab code
  ## was crushing I don't know if I didnt destroy something :)

    data = dlmread('Siatka/trian.txt',' ');
    ## data(:,3)=[];
    mesh.t=data+1;

    data = dlmread('Siatka/points.txt',' ');
    ## data(:,2:3)=[];
    mesh.p=data/100;

    data = dlmread('Siatka/boundIndx.txt',' ');
    mesh.t_boundary=data+1;

    data = dlmread('Siatka/bound.txt',' ');
    ## data(:,2:3)=[];
    mesh.p_boundary=data/100;

    data = dlmread('Siatka/enterIndx.txt',' ');
    mesh.t_enter=data+1;

    data = dlmread('Siatka/enter.txt',' ');
    ## data(:,2:3)=[];
    mesh.p_enter=data/100;

    data = dlmread('Siatka/exitIndx.txt',' ');
    mesh.t_exit=data+1;

    data = dlmread('Siatka/exit.txt',' ');
    ## data(:,2:3)=[];
    mesh.p_exit=data/100;

    data = dlmread('Siatka/freeIndx.txt',' ');
    mesh.t_free=data+1;

    data = dlmread('Siatka/free.txt',' ');
    ## data(:,2:3)=[];
    mesh.p_free=data/100;


    save Tomasz_Mesh mesh
end
