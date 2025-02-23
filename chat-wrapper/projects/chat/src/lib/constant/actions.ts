export const actions = {
  generate_model: {
    "description": "Generate a model",
    "api_endpoint": "http://your-internal-api.com/generate-model",
    "method": "POST",
  },
  duplicate_model: {
    "description": "Duplicate a model",
    "api_endpoint": "http://your-internal-api.com/restart-service",
    "method": "POST",
  },
  delete_model: {
    "description": "Delete a model",
    "api_endpoint": "http://your-internal-api.com/restart-service",
    "method": "POST",
  },
  deploy_model: {
    "description": "Deploy a model",
    "api_endpoint": "http://your-internal-api.com/deploy",
    "method": "POST",
  },
};

export type ActionKeys = keyof typeof actions;
