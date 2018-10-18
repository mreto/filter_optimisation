function Load_Points(id)

  ## IMPORTANT NOTE I have commented all the data... lines without it the matlab code
  ## was crushing I don't know if I didnt destroy something :)

    path = ['Siatka/', id];
    data = dlmread([path '_trian.txt'],' ');
    ## data(:,3)=[];
    mesh.t=data+1;

    data = dlmread([path, '_points.txt'],' ');
    ## data(:,2:3)=[];
    mesh.p=data/100;

    data = dlmread([path, '_boundIndx.txt'],' ');
    mesh.t_boundary=data+1;

    data = dlmread([path, '_bound.txt'],' ');
    ## data(:,2:3)=[];
    mesh.p_boundary=data/100;

    data = dlmread([path, '_enterIndx.txt'],' ');
    mesh.t_enter=data+1;

    data = dlmread([path, '_enter.txt'],' ');
    ## data(:,2:3)=[];
    mesh.p_enter=data/100;

    data = dlmread([path, '_exitIndx.txt'],' ');
    mesh.t_exit=data+1;

    data = dlmread([path, '_exit.txt'],' ');
    ## data(:,2:3)=[];
    mesh.p_exit=data/100;

    data = dlmread([path, '_freeIndx.txt'],' ');
    mesh.t_free=data+1;

    data = dlmread([path, '_free.txt'],' ');
    ## data(:,2:3)=[];
    mesh.p_free=data/100;


    save_string = ['Tomasz_Mesh_', id];
    save(save_string, 'mesh')
end
