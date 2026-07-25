import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-[#F8F6F3] px-6">
          <div className="text-center max-w-md">
            <div className="w-14 h-14 rounded-full bg-[#EBF0F5] flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-[#1A3C5E]">!</span>
            </div>
            <h1 className="text-lg font-bold text-[#1C1917]">Something went wrong</h1>
            <p className="text-sm text-[#6B6560] mt-2">{this.state.error?.message || "An unexpected error occurred."}</p>
            <button
              onClick={() => { this.setState({ hasError: false, error: null }); window.location.href = "/"; }}
              className="mt-6 px-5 py-2 rounded-lg bg-[#1A3C5E] text-white text-sm font-medium hover:bg-[#2E5C8A]"
            >
              Go home
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
