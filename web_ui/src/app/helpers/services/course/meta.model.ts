import { MetaDataI } from "./course.interface";

export class MetaManager {
    metaData: MetaDataI = {};

    constructor(resp: MetaDataI) {
        this.metaData = resp;
    }

    getEstimatedTime(cellIDs: string[]) {
        let time = 0;

        const addedLO = new Set();

        while (cellIDs.length) {
            const id = cellIDs.pop();
            if (!id) { break }
            const metaData = this.metaData[id];

            if (!addedLO.has(id)) {
                if (metaData) {
                    time += +metaData.cell_estimated_time;
                }
                addedLO.add(id)
            }

            if (metaData) {
                metaData.cell_prereqs.forEach((pre) => {
                    if (!addedLO.has(pre)) {
                        cellIDs.push(pre);
                    }
                })
            }
        }

        return time
    }
}