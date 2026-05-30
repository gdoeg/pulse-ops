"use client";

import { Component, ReactNode } from "react";
import { AlertTriangle } from "lucide-react";

import { Button } from "components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "components/ui/card";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class DashboardErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  override componentDidCatch(error: Error) {
    console.error(error);
  }

  private handleReset = () => {
    this.setState({ hasError: false });
  };

  override render() {
    if (this.state.hasError) {
      return (
        <main className="mx-auto flex min-h-screen w-full max-w-7xl items-center justify-center px-4 py-10 sm:px-6 lg:px-8">
          <Card className="w-full max-w-xl">
            <CardHeader>
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-rose-500/10 text-rose-300">
                <AlertTriangle className="h-6 w-6" />
              </div>
              <CardTitle>Observability workspace crashed</CardTitle>
              <CardDescription>PulseOps recovered safely. Retry to render the dashboard again.</CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={this.handleReset}>Reload workspace</Button>
            </CardContent>
          </Card>
        </main>
      );
    }

    return this.props.children;
  }
}
