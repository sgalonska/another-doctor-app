import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold tracking-tight mb-4">
            Find the Right Medical Specialist
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            Upload your medical records and get matched with specialists who have expertise in your specific condition
          </p>
          <Button size="lg" className="mr-4">
            Upload Records
          </Button>
          <Button variant="outline" size="lg">
            Learn More
          </Button>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Upload & Parse</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Upload your medical reports or paste text. Our system extracts key information while keeping your data secure.
              </CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Expert Matching</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                We analyze published research, clinical trials, and expertise to find specialists who match your specific condition.
              </CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Connect</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Get introduced to 2-3 carefully selected specialists with detailed profiles and evidence of their expertise.
              </CardDescription>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}