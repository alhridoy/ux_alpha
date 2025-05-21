
import React, { useState } from 'react';
import { z } from 'zod';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { Loader2, Download } from 'lucide-react';
import { backendService } from '@/services/backendService';

interface DataExtractionFormProps {
  webUrl: string;
  onDataExtracted?: (data: any) => void;
}

type SchemaField = {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  description: string;
};

const DataExtractionForm: React.FC<DataExtractionFormProps> = ({ webUrl, onDataExtracted }) => {
  const [instruction, setInstruction] = useState('');
  const [fields, setFields] = useState<SchemaField[]>([
    { name: '', type: 'string', description: '' }
  ]);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractedData, setExtractedData] = useState<any>(null);

  const addField = () => {
    setFields([...fields, { name: '', type: 'string', description: '' }]);
  };

  const updateField = (index: number, field: Partial<SchemaField>) => {
    const newFields = [...fields];
    newFields[index] = { ...newFields[index], ...field };
    setFields(newFields);
  };

  const removeField = (index: number) => {
    if (fields.length === 1) return;
    setFields(fields.filter((_, i) => i !== index));
  };

  const handleExtract = async () => {
    if (!instruction.trim()) {
      toast.error('Please provide an extraction instruction');
      return;
    }

    if (fields.some(field => !field.name.trim())) {
      toast.error('All schema fields must have a name');
      return;
    }

    // Build schema definition
    const schemaDefinition = {
      type: 'object',
      properties: Object.fromEntries(
        fields.map(field => [
          field.name,
          {
            type: field.type,
            description: field.description,
          },
        ])
      ),
      required: fields.map(field => field.name),
    };

    setIsExtracting(true);
    
    try {
      const data = await backendService.extractWithStagehand(webUrl, instruction, schemaDefinition);
      
      setExtractedData(data);
      if (onDataExtracted) {
        onDataExtracted(data);
      }
      
      toast.success('Data extracted successfully');
    } catch (error) {
      console.error('Extraction error:', error);
      toast.error('Failed to extract data');
    } finally {
      setIsExtracting(false);
    }
  };

  const downloadJson = () => {
    if (!extractedData) return;
    
    const dataStr = JSON.stringify(extractedData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const downloadLink = document.createElement('a');
    downloadLink.setAttribute('href', dataUri);
    downloadLink.setAttribute('download', 'extracted_data.json');
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
  };

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>Extract Data with Stagehand AI</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Extraction Instruction</label>
          <Textarea 
            placeholder="E.g., Extract product names and prices from this e-commerce page"
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            className="min-h-[80px]"
          />
        </div>
        
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Schema Definition</label>
            <Button type="button" variant="outline" size="sm" onClick={addField}>
              Add Field
            </Button>
          </div>
          <div className="space-y-3">
            {fields.map((field, index) => (
              <div key={index} className="flex items-end gap-2 border p-3 rounded-md">
                <div className="flex-1">
                  <label className="text-xs text-muted-foreground">Field Name</label>
                  <Input 
                    value={field.name}
                    onChange={(e) => updateField(index, { name: e.target.value })}
                    placeholder="productName"
                    className="mt-1"
                  />
                </div>
                <div className="w-32">
                  <label className="text-xs text-muted-foreground">Type</label>
                  <select 
                    value={field.type}
                    onChange={(e) => updateField(index, { type: e.target.value as any })}
                    className="mt-1 w-full h-10 px-3 py-2 bg-background border border-input rounded-md"
                  >
                    <option value="string">String</option>
                    <option value="number">Number</option>
                    <option value="boolean">Boolean</option>
                    <option value="array">Array</option>
                    <option value="object">Object</option>
                  </select>
                </div>
                <div className="flex-1">
                  <label className="text-xs text-muted-foreground">Description (Optional)</label>
                  <Input 
                    value={field.description}
                    onChange={(e) => updateField(index, { description: e.target.value })}
                    placeholder="Product name as displayed"
                    className="mt-1"
                  />
                </div>
                {fields.length > 1 && (
                  <Button 
                    type="button" 
                    variant="outline" 
                    size="sm" 
                    onClick={() => removeField(index)}
                    className="flex-shrink-0 h-10"
                  >
                    Remove
                  </Button>
                )}
              </div>
            ))}
          </div>
        </div>
        
        {extractedData && (
          <div className="mt-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Extracted Data</h3>
              <Button variant="outline" size="sm" onClick={downloadJson}>
                <Download className="h-4 w-4 mr-2" />
                Download JSON
              </Button>
            </div>
            <pre className="bg-slate-50 p-4 rounded-md mt-2 overflow-auto max-h-[300px] text-sm">
              {JSON.stringify(extractedData, null, 2)}
            </pre>
          </div>
        )}
      </CardContent>
      <CardFooter>
        <Button
          onClick={handleExtract}
          disabled={isExtracting || !instruction.trim() || fields.some(field => !field.name.trim())}
          className="w-full"
        >
          {isExtracting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Extracting Data...
            </>
          ) : (
            'Extract Data'
          )}
        </Button>
      </CardFooter>
    </Card>
  );
};

export default DataExtractionForm;
