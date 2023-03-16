/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Image } from '../models/Image';
import type { ImageDigest } from '../models/ImageDigest';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class ImageService {

    /**
     * Get
     * @returns ImageDigest Successful Response
     * @throws ApiError
     */
    public static getImageGet({
wsName,
start,
end,
keyword,
orderBy = 'id',
order = 'asc',
}: {
wsName: string,
start: number,
end: number,
keyword?: string,
orderBy?: 'id' | 'date' | 'random',
order?: 'asc' | 'desc',
}): CancelablePromise<Array<ImageDigest>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/image/',
            query: {
                'ws_name': wsName,
                'start': start,
                'end': end,
                'keyword': keyword,
                'order_by': orderBy,
                'order': order,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Similar Images
     * @returns ImageDigest Successful Response
     * @throws ApiError
     */
    public static getSimilarImagesImageSimilarGet({
workspace,
start,
end,
queryIds,
keyword,
orderBy = 'similarity',
order = 'desc',
}: {
workspace: string,
start: number,
end: number,
queryIds: Array<string>,
keyword?: string,
orderBy?: 'similarity',
order?: 'asc' | 'desc',
}): CancelablePromise<Array<ImageDigest>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/image/similar',
            query: {
                'workspace': workspace,
                'start': start,
                'end': end,
                'keyword': keyword,
                'query_ids': queryIds,
                'order_by': orderBy,
                'order': order,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Find
     * @returns Image Successful Response
     * @throws ApiError
     */
    public static findImageFindGet({
imageId,
}: {
imageId: string,
}): CancelablePromise<Image> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/image/find',
            query: {
                'image_id': imageId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get File
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getFileImageFileGet({
imageId,
imageType = 'original',
}: {
imageId: string,
imageType?: 'original' | 'thumbnail',
}): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/image/file',
            query: {
                'image_id': imageId,
                'image_type': imageType,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Tags Map Jp
     * @returns string Successful Response
     * @throws ApiError
     */
    public static getTagsMapJpImageTagsMapJpGet(): CancelablePromise<Record<string, string>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/image/tags/map/jp',
        });
    }

}
