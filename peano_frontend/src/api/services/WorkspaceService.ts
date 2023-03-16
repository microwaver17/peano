/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ResultResponse } from '../models/ResultResponse';
import type { Workspace } from '../models/Workspace';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class WorkspaceService {

    /**
     * Find
     * @returns Workspace Successful Response
     * @throws ApiError
     */
    public static findWorkspaceFindGet({
wsName,
}: {
wsName: string,
}): CancelablePromise<Workspace> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/workspace/find',
            query: {
                'ws_name': wsName,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get
     * @returns Workspace Successful Response
     * @throws ApiError
     */
    public static getWorkspaceGet(): CancelablePromise<Record<string, Workspace>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/workspace/',
        });
    }

    /**
     * Update
     * @returns ResultResponse Successful Response
     * @throws ApiError
     */
    public static updateWorkspaceUpdatePost({
requestBody,
}: {
requestBody: Workspace,
}): CancelablePromise<ResultResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/workspace/update',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create
     * @returns ResultResponse Successful Response
     * @throws ApiError
     */
    public static createWorkspaceCreatePost({
requestBody,
}: {
requestBody: Workspace,
}): CancelablePromise<ResultResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/workspace/create',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete
     * @returns ResultResponse Successful Response
     * @throws ApiError
     */
    public static deleteWorkspaceDeletePost({
requestBody,
}: {
requestBody: Workspace,
}): CancelablePromise<ResultResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/workspace/delete',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
