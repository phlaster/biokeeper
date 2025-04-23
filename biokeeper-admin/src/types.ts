
export interface CartItemInterface {
    id: number;
    product_id: number;
    quantity: number;
    customization_features: Record<string, any>;
    name: string;
    price: number;
    photo: string;
    added_at: Date;
    product_type_name: string;
    product_slug: string;
}

export interface CartItemStoreInterface {
    id: number;
    product_id: number;
    quantity: number;
    customization_features: Record<string, any>;
    added_at: Date;
}

export interface ProductInterface {
    id: number;
    name: string;
    slug: string;
    price: number;
    photos: { id: number; is_main: boolean; }[];
}