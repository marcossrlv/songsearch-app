import React from 'react';
import { useNavigate } from 'react-router-dom';

const Result = () => {
    const navigate = useNavigate();

    const track = {
        title: "360",
        artist: "Charli XCX",
        album: "brat",
        year: "2024",
        cover: "https://t2.genius.com/unsafe/1300x0/https%3A%2F%2Fimages.genius.com%2F34d321744a8e728edcf34085725dd61e.1000x1000x1.png",
        texto: "Brat es el sexto álbum de estudio de la cantautora británica Charli XCX, lanzado el 7 de junio de 2024 bajo el sello de Atlantic Records. La cantante anunció el disco el 28 de febrero de 2024 y al día siguiente fue publicado «Von Dutch» como sencillo."
    };

    const goBack = () => {
        navigate('/welcome');
    }

    return (
        <div className='background'>
            <div className='contenedor'>
                <div className='imagen'>
                    <img src={track.cover} width={200} height={200}></img>
                    <p>{track.title} - {track.artist}</p>
                    <p>{track.album}</p>
                </div>
                <div className='texto'>
                    <p>{track.texto}</p>
                </div>
                <button onClick={goBack}>{"<"}</button>
                <button>{"Try again :)"}</button>
            </div>
        </div>
    );
}

export default Result;