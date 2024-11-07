// 1. 동기 import 사용
import { getHeatMap } from 'youtube-heatmap';

// 2. getHeatMap 함수 호출
getHeatMap('https://www.youtube.com/watch?v=_lEzN8C5c7k')
    .then(heatMap => {
        console.log(heatMap);
    })
    .catch(error => {
        console.error("Error fetching heat map:", error);
    });
