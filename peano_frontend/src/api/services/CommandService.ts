/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ResultResponse } from '../models/ResultResponse';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class CommandService {

    /**
     * Do Dirscan
     * @returns ResultResponse Successful Response
     * @throws ApiError
     */
    public static doDirscanCommandDirscanScanPost({
wsName,
}: {
wsName: string,
}): CancelablePromise<ResultResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/command/dirscan/scan',
            query: {
                'ws_name': wsName,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Stop Dirscan
     * @returns ResultResponse Successful Response
     * @throws ApiError
     */
    public static stopDirscanCommandDirscanScanStopPost(): CancelablePromise<ResultResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/command/dirscan/scan/stop',
        });
    }

    /**
     * Do Mlscan
     * @returns ResultResponse Successful Response
     * @throws ApiError
     */
    public static doMlscanCommandMlscanScanPost({
wsName,
}: {
wsName: string,
}): CancelablePromise<ResultResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/command/mlscan/scan',
            query: {
                'ws_name': wsName,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Stop Mlscan
     * @returns ResultResponse Successful Response
     * @throws ApiError
     */
    public static stopMlscanCommandMlscanScanStopPost(): CancelablePromise<ResultResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/command/mlscan/scan/stop',
        });
    }

    /**
     * Do Preprocess
     * @returns ResultResponse Successful Response
     * @throws ApiError
     */
    public static doPreprocessCommandMlscanPreprocessPost({
wsName,
}: {
wsName: string,
}): CancelablePromise<ResultResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/command/mlscan/preprocess',
            query: {
                'ws_name': wsName,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Fix Db
     * @returns any Successful Response
     * @throws ApiError
     */
    public static fixDbCommandDbFixPost(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/command/db/fix',
        });
    }

}
