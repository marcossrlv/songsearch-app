import React, { useEffect, useState } from 'react';

const LyricsCard = ({track, chunks, openDialog, closeDialog}) => {

    const resaltarTexto = (lyrics, chunks) => {
        if (!lyrics || !chunks) return lyrics;
        // Escapar caracteres especiales
        const escaparRegex = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(
            chunks.map(chunk => escaparRegex(chunk)).join('|'), // Combina las partes con "|"
            'gi'
        );
        // Reemplazar la coincidencia con <mark>
        return lyrics.replace(regex, (match) => `<mark class="bg-green-300 text-black font-bold rounded px-1">${match}</mark>`);
    };

    const partesAResaltar = Array.isArray(chunks) ? chunks.map(chunk => chunk.lyrics) : [];

    const letraResaltada = resaltarTexto(track.lyrics, partesAResaltar);

    return(
        <dialog className='modal' open={openDialog} onClose={closeDialog}>
            <div className="modal-box">
                <h3 className="font-bold text-lg">{track.title} - {track.artist}</h3>
                <div className="py-4 whitespace-pre-line">  
                    <p dangerouslySetInnerHTML={{ __html: letraResaltada }}></p>
                </div>
            </div>
            <form method="dialog" className="modal-backdrop">
                <button>close</button>
            </form>
        </dialog>
    );
}

export default LyricsCard;