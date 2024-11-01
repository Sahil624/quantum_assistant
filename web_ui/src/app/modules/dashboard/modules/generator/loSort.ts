import { MetaDataI } from "../../../../helpers/services/course/course.interface";

/**
 * Sorts the selected Learning Objects based on their order in the available Learning Objects list.
 * Unknown LOs are placed at the end of their respective modules.
 * @param availableLOsResp - Array of all available Learning Objects in their original order.
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

    // Create a Map to store LOs by module
    const moduleMap = new Map<string, string[]>();
    availableLOs.forEach(lo => {
        const module = getModulePrefix(lo);
        if (!moduleMap.has(module)) {
            moduleMap.set(module, []);
        }
        moduleMap.get(module)?.push(lo);
    });

    // Group selected LOs by module
    const selectedByModule = new Map<string, string[]>();
    selectedLOs.forEach(lo => {
        const module = getModulePrefix(lo);
        if (!selectedByModule.has(module)) {
            selectedByModule.set(module, []);
        }
        selectedByModule.get(module)?.push(lo);
    });

    // Sort LOs within each module
    const sortedLOs: string[] = [];
    
    // Get all unique modules from both available and selected LOs
    const allModules = new Set([
        ...Array.from(moduleMap.keys()),
        ...Array.from(selectedByModule.keys())
    ]);

    // Sort modules to maintain module order
    const sortedModules = Array.from(allModules).sort((a, b) => {
        const firstLOofModuleA = moduleMap.get(a)?.[0];
        const firstLOofModuleB = moduleMap.get(b)?.[0];
        const indexA = firstLOofModuleA ? loOrder.get(firstLOofModuleA) ?? Infinity : Infinity;
        const indexB = firstLOofModuleB ? loOrder.get(firstLOofModuleB) ?? Infinity : Infinity;
        return indexA - indexB;
    });

    // Process each module
    sortedModules.forEach(module => {
        const moduleLOs = selectedByModule.get(module) || [];
        
        // Split LOs into known and unknown
        const known = moduleLOs.filter(lo => loOrder.has(lo));
        const unknown = moduleLOs.filter(lo => !loOrder.has(lo));
        
        // Sort known LOs by their original order
        const sortedKnown = known.sort((a, b) => {
            const indexA = loOrder.get(a) ?? Infinity;
            const indexB = loOrder.get(b) ?? Infinity;
            return indexA - indexB;
        });
        
        // Append unknown LOs after known ones for this module
        sortedLOs.push(...sortedKnown, ...unknown);
    });

    return sortedLOs;
}