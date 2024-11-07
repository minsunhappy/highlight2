// heatmap.js
import { getHeatMap } from 'youtube-heatmap';

async function fetchHeatMap(videoId) {
    try {
        const heatMap = await getHeatMap(`https://www.youtube.com/watch?v=${videoId}`);
        console.log(JSON.stringify({ videoId, heatMap }));
    } catch (error) {
        console.error("Error fetching heat map:", error);
    }
}

const videoId = process.argv[2];
fetchHeatMap(videoId);
