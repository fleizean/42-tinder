interface Config {
    api: {
      url: string;
    };
  }
  
  const config: Config = {
    api: {
      url: process.env.BACKEND_API_URL || 'http://localhost:5187'
    }
  };
  
  export default config;