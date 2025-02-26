
export interface IFile {
    title: string;
    src: string;
    rawFile?: File;
    extra?: {[name: string]: string | number | boolean | null};
}


export interface IFileUploadProvider {
    upload(resource: string, fields: { [name: string]: IFile }): Promise<{ [name: string]: IFile }>
}


export class DefaultFileUploadProvider implements IFileUploadProvider {
    async upload(resource: string, fields: { [name: string]: IFile }): Promise<{ [name: string]: IFile }> {
        const new_fields: { [name: string]: IFile } = {};
        for (const name in fields) {
            const file = fields[name];
            if (file.rawFile instanceof File) {
                new_fields[name] = await convertFileToBase64(file);
            }
        }
        return new_fields;
    }
}


/**
 * Convert a `File` object returned by the upload input into a base 64 string.
 * That's not the most optimized way to store images in production, but it's
 * enough to illustrate the idea of dataprovider decoration.
 */
function convertFileToBase64(file: IFile): Promise<IFile> {
    if (file.rawFile !== undefined) {
        const rawFile = file.rawFile;
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                if (typeof reader.result === "string") {
                    resolve({
                        src: reader.result,
                        title: file.title,
                    });
                } else {
                    resolve({
                        src: "",
                        title: file.title,
                    });
                }
            };
            reader.onerror = reject;
            reader.readAsDataURL(rawFile);
        });
    }
    return Promise.resolve({
        src: "",
        title: file.title,
    });
}
