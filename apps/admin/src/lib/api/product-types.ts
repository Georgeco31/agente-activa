export interface Product {
  id: string;
  sku: string;
  name: string;
  normalized_name: string;
  description: string | null;
  unit: string;
  price: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductCreateInput {
  sku: string;
  name: string;
  description?: string | null;
  unit: string;
  price: string;
  is_active?: boolean;
}

export interface ProductUpdateInput {
  sku?: string;
  name?: string;
  description?: string | null;
  unit?: string;
  price?: string;
  is_active?: boolean;
}

export type ProductSearchResult = Product;
export type ProductDeactivateResult = Product;

export interface ProductSearchCriteria {
  name?: string;
  sku?: string;
}
