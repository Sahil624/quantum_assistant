import { AvailableLOResponse, MetaDataI } from "../../../../helpers/services/course/course.interface";

/**
 * Sorts the selected Learning Objects based on their order in the available Learning Objects list.
 * @param availableLOs - Array of all available Learning Objects in their original order.
 * @param selectedLOs - Array of Learning Objects that need to be sorted.
 * @returns A new array with the selected LOs sorted according to their order in the available LOs list.
 */
export function sortLearningObjects(availableLOsResp: MetaDataI, selectedLOs: string[]): string[] {
    const availableLOs = Object.keys(availableLOsResp);
      // Create a Map to store the index of each available LO
      const loOrder = new Map<string, number>(
        availableLOs.map((lo, index) => [lo, index])
    );

    // Function to get the module prefix of an LO
    const getModulePrefix = (lo: string): string => lo.split('-')[0];

    // Create a Map to store the last known index for each module
    const lastKnownModuleIndex = new Map<string, number>();

    // Populate lastKnownModuleIndex
    availableLOs.forEach((lo, index) => {
        const modulePrefix = getModulePrefix(lo);
        lastKnownModuleIndex.set(modulePrefix, index);
    });

    // Sort the selected LOs
    const sortedLOs = selectedLOs.sort((a, b) => {
        const indexA = loOrder.get(a);
        const indexB = loOrder.get(b);

        if (indexA !== undefined && indexB !== undefined) {
            return indexA - indexB;
        }

        if (indexA !== undefined) return -1;
        if (indexB !== undefined) return 1;

        // Both LOs are unknown, sort them based on their module's last known index
        const moduleA = getModulePrefix(a);
        const moduleB = getModulePrefix(b);
        const lastIndexA = lastKnownModuleIndex.get(moduleA) ?? Number.POSITIVE_INFINITY;
        const lastIndexB = lastKnownModuleIndex.get(moduleB) ?? Number.POSITIVE_INFINITY;
        
        return lastIndexA - lastIndexB;
    });

    return sortedLOs;
}
