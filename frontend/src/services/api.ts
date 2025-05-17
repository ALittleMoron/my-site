import axios from "axios";

// Create axios instance with default config
const apiClient = axios.create({
  headers: {
    "Content-Type": "application/json",
  },
});

// Add response interceptor for logging
apiClient.interceptors.response.use(
  (response) => {
    console.log("API Response:", {
      url: response.config.url,
      method: response.config.method,
      status: response.status,
      data: response.data,
      headers: response.headers,
    });
    return response;
  },
  (error) => {
    console.error("API Error:", {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      headers: error.response?.headers,
      message: error.message,
      stack: error.stack,
    });
    return Promise.reject(error);
  }
);

// Add request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log("API Request:", {
      url: config.url,
      method: config.method,
      headers: config.headers,
      params: config.params,
      baseURL: config.baseURL,
    });
    return config;
  },
  (error) => {
    console.error("API Request Error:", error);
    return Promise.reject(error);
  }
);

export interface CompetencyMatrixSheet {
  sheets: string[];
}

export interface CompetencyMatrixItemShort {
  id: number;
  question: string;
}

export interface CompetencyMatrixItemDetailed
  extends CompetencyMatrixItemShort {
  answer: string;
  interviewExpectedAnswer: string;
  sheet: string;
  grade: string;
  section: string;
  subsection: string;
  resources: {
    id: number;
    name: string;
    url: string;
    context: string;
  }[];
}

export interface CompetencyMatrixItemsResponse {
  sheet: string;
  sections: {
    section: string;
    subsections: {
      subsection: string;
      grades: {
        grade: string;
        items: CompetencyMatrixItemShort[];
      }[];
    }[];
  }[];
}

export const api = {
  getSheets: async (): Promise<CompetencyMatrixSheet> => {
    try {
      console.log("Fetching sheets from:", `/api/competency-matrix/sheets/`);
      const response = await apiClient.get("/api/competency-matrix/sheets/");
      return response.data;
    } catch (error) {
      console.error("Error fetching sheets:", error);
      throw error;
    }
  },

  getItems: async (
    sheetName: string
  ): Promise<CompetencyMatrixItemsResponse> => {
    try {
      console.log("Fetching items for sheet:", sheetName);
      const response = await apiClient.get("/api/competency-matrix/items/", {
        params: { sheetName },
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching items:", error);
      throw error;
    }
  },

  getItem: async (id: number): Promise<CompetencyMatrixItemDetailed> => {
    try {
      console.log("Fetching item with ID:", id);
      const response = await apiClient.get(
        `/api/competency-matrix/items/${id}/`
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching item:", error);
      throw error;
    }
  },
};
